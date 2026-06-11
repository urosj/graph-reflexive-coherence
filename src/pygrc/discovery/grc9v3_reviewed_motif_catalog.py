"""Reviewed motif catalog generation for GRC9V3 phenomenology discovery."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any

from .grc9_manifest import is_session_id


GRC9V3_REVIEWED_MOTIF_CATALOG_VERSION = "grc9v3_reviewed_motif_catalog_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9v3/phenomenology_discovery/sessions")
EXPERIMENTAL_LOG_PATH = Path("outputs/grc9v3/phenomenology_discovery/ExperimentalLog.md")
_REVIEW_TIMESTAMP_UTC = "2026-04-26T00:00:00Z"
_REVIEWER = "phase_i09_review_policy"
_BASE_NON_CLAIMS = (
    "no_grcl9_source_lowering_claim",
    "no_lorentzian_causal_layer_claim",
    "no_visual_only_promotion",
)
_LIFECYCLE_FIELD_FRAGMENTS = (
    "lifecycle_event_counts.hybrid_spark_candidate_count",
    "lifecycle_event_counts.hybrid_mechanical_expansion_count",
    "lifecycle_event_counts.hybrid_spark_completed_count",
    "lifecycle_event_counts.growth_count",
    "lifecycle_event_counts.collapse_count",
)


@dataclass(frozen=True)
class GRC9V3ReviewHistoryEntry:
    motif_id: str
    from_status: str
    to_status: str
    reason: str
    reviewer: str
    timestamp_utc: str

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "motif_id": self.motif_id,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "reason": self.reason,
            "reviewer": self.reviewer,
            "timestamp_utc": self.timestamp_utc,
        }


@dataclass(frozen=True)
class GRC9V3ReviewedMotifRecord:
    motif_id: str
    lane_name: str
    phenomenon: str
    profile: str
    seed_name: str
    run_id: str
    source_session_ids: tuple[str, ...]
    step_window: tuple[int, int]
    control_role: str
    confidence_score: int
    confidence_label: str
    source_review_status: str
    review_status: str
    catalog_category: str
    event_motif_eligible: bool
    predicted_evidence_fields: tuple[str, ...]
    observed_evidence_fields: tuple[str, ...]
    missing_surface_fields: tuple[str, ...]
    visual_artifacts: tuple[str, ...]
    checkpoint_links: tuple[Mapping[str, Any], ...]
    telemetry_artifact_root: str
    event_sequence_delta: Mapping[str, Any] | None
    non_claims: tuple[str, ...]
    rejection_reason: str | None = None
    rerun_requested: bool = False
    duplicate_of: str | None = None
    review_notes: Mapping[str, Any] = None

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "motif_id": self.motif_id,
            "lane_name": self.lane_name,
            "phenomenon": self.phenomenon,
            "profile": self.profile,
            "seed_name": self.seed_name,
            "run_id": self.run_id,
            "source_session_ids": list(self.source_session_ids),
            "step_window": list(self.step_window),
            "control_role": self.control_role,
            "confidence_score": self.confidence_score,
            "confidence_label": self.confidence_label,
            "source_review_status": self.source_review_status,
            "review_status": self.review_status,
            "catalog_category": self.catalog_category,
            "event_motif_eligible": self.event_motif_eligible,
            "predicted_evidence_fields": list(self.predicted_evidence_fields),
            "observed_evidence_fields": list(self.observed_evidence_fields),
            "missing_surface_fields": list(self.missing_surface_fields),
            "visual_artifacts": list(self.visual_artifacts),
            "checkpoint_links": [dict(item) for item in self.checkpoint_links],
            "telemetry_artifact_root": self.telemetry_artifact_root,
            "event_sequence_delta": (
                None if self.event_sequence_delta is None else dict(self.event_sequence_delta)
            ),
            "non_claims": list(self.non_claims),
            "rejection_reason": self.rejection_reason,
            "rerun_requested": self.rerun_requested,
            "duplicate_of": self.duplicate_of,
            "review_notes": dict(self.review_notes or {}),
        }


@dataclass(frozen=True)
class GRC9V3ReviewedMotifCatalogSession:
    session_id: str
    selector_session_id: str
    visual_session_id: str
    hessian_review_session_id: str
    records: tuple[GRC9V3ReviewedMotifRecord, ...]
    diagnostic_records: tuple[Mapping[str, Any], ...]
    review_history: tuple[GRC9V3ReviewHistoryEntry, ...]
    reviewed_catalog_path: str
    markdown_catalog_path: str
    report_path: str

    def to_mapping(self) -> Mapping[str, Any]:
        status_counts = Counter(record.review_status for record in self.records)
        category_counts = Counter(record.catalog_category for record in self.records)
        return {
            "session_id": self.session_id,
            "version": GRC9V3_REVIEWED_MOTIF_CATALOG_VERSION,
            "selector_session_id": self.selector_session_id,
            "visual_session_id": self.visual_session_id,
            "hessian_review_session_id": self.hessian_review_session_id,
            "motif_count": len(self.records),
            "diagnostic_record_count": len(self.diagnostic_records),
            "review_history_count": len(self.review_history),
            "review_status_counts": dict(sorted(status_counts.items())),
            "catalog_category_counts": dict(sorted(category_counts.items())),
            "accepted_count": status_counts.get("accepted", 0),
            "strong_candidate_count": status_counts.get("strong_candidate", 0),
            "diagnostic_comparator_count": status_counts.get("diagnostic_comparator", 0),
            "rejected_count": status_counts.get("rejected", 0),
            "duplicate_count": status_counts.get("duplicate", 0),
            "needs_rerun_count": status_counts.get("needs-rerun", 0),
            "event_motif_eligible_count": sum(
                1 for record in self.records if record.event_motif_eligible
            ),
            "visual_linked_record_count": sum(
                1 for record in self.records if record.visual_artifacts
            ),
            "checkpoint_linked_record_count": sum(
                1 for record in self.records if record.checkpoint_links
            ),
            "records": [record.to_mapping() for record in self.records],
            "diagnostic_records": [dict(record) for record in self.diagnostic_records],
            "review_history": [entry.to_mapping() for entry in self.review_history],
            "reviewed_catalog_path": self.reviewed_catalog_path,
            "markdown_catalog_path": self.markdown_catalog_path,
            "report_path": self.report_path,
        }


def run_grc9v3_reviewed_motif_catalog(
    *,
    session_id: str = "S0012",
    selector_session_id: str = "S0009",
    visual_session_id: str = "S0010",
    hessian_review_session_id: str = "S0011",
    session_root: str | Path | None = None,
    selector_manifest_path: str | Path | None = None,
    selector_report_path: str | Path | None = None,
    visual_index_path: str | Path | None = None,
    hessian_review_path: str | Path | None = None,
    reviewer: str = _REVIEWER,
    review_timestamp_utc: str = _REVIEW_TIMESTAMP_UTC,
    update_experimental_log: bool = True,
) -> GRC9V3ReviewedMotifCatalogSession:
    """Review GRC9V3 selector candidates and emit a stable motif catalog."""

    for value in (session_id, selector_session_id, visual_session_id, hessian_review_session_id):
        if not is_session_id(value):
            raise ValueError("session ids must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    selector_manifest = _read_required_json(
        Path(selector_manifest_path)
        if selector_manifest_path is not None
        else DISCOVERY_SESSION_ROOT / selector_session_id / "selector_manifest.json",
        "selector manifest",
    )
    selector_report = _read_required_json(
        Path(selector_report_path)
        if selector_report_path is not None
        else DISCOVERY_SESSION_ROOT
        / selector_session_id
        / "reports"
        / "selector_validation_report.json",
        "selector validation report",
    )
    visual_index = _read_required_json(
        Path(visual_index_path)
        if visual_index_path is not None
        else DISCOVERY_SESSION_ROOT / visual_session_id / "visual_index.json",
        "visual index",
    )
    hessian_review = _read_required_json(
        Path(hessian_review_path)
        if hessian_review_path is not None
        else DISCOVERY_SESSION_ROOT
        / hessian_review_session_id
        / "hessian_comparator_review.json",
        "Hessian comparator review",
    )

    records, review_history = _review_records(
        selector_manifest=selector_manifest,
        selector_report=selector_report,
        visual_index=visual_index,
        hessian_review=hessian_review,
        reviewer=reviewer,
        review_timestamp_utc=review_timestamp_utc,
    )
    reviewed_catalog_path = root / "reviewed_motif_catalog.json"
    markdown_catalog_path = root / "reviewed_motif_catalog.md"
    report_path = reports_root / "reviewed_motif_catalog_report.json"
    session = GRC9V3ReviewedMotifCatalogSession(
        session_id=session_id,
        selector_session_id=selector_session_id,
        visual_session_id=visual_session_id,
        hessian_review_session_id=hessian_review_session_id,
        records=tuple(records),
        diagnostic_records=tuple(hessian_review.get("pair_reviews", ())),
        review_history=tuple(review_history),
        reviewed_catalog_path=str(reviewed_catalog_path),
        markdown_catalog_path=str(markdown_catalog_path),
        report_path=str(report_path),
    )
    _write_json(reviewed_catalog_path, _catalog_payload(session))
    _write_markdown_catalog(markdown_catalog_path, session)
    _write_json(report_path, session.to_mapping())
    _write_json(root / "session_manifest.json", _session_manifest(session))
    _write_summary_markdown(reports_root / "reviewed_motif_catalog_summary.md", session)
    _write_readme(root, session)
    if update_experimental_log and session_root is None:
        _append_experimental_log(session)
    return session


def _review_records(
    *,
    selector_manifest: Mapping[str, Any],
    selector_report: Mapping[str, Any],
    visual_index: Mapping[str, Any],
    hessian_review: Mapping[str, Any],
    reviewer: str,
    review_timestamp_utc: str,
) -> tuple[list[GRC9V3ReviewedMotifRecord], list[GRC9V3ReviewHistoryEntry]]:
    validations = {
        str(item.get("lane_name")): item
        for item in selector_report.get("validations", ())
        if isinstance(item, Mapping) and item.get("lane_name")
    }
    visual_records = {
        str(item.get("lane_name")): item
        for item in visual_index.get("records", ())
        if isinstance(item, Mapping) and item.get("lane_name")
    }
    hessian_lanes = {
        str(item.get("lane_name")): item
        for item in hessian_review.get("lane_reviews", ())
        if isinstance(item, Mapping) and item.get("lane_name")
    }
    reviewed_records: list[GRC9V3ReviewedMotifRecord] = []
    history: list[GRC9V3ReviewHistoryEntry] = []
    seen_keys: dict[tuple[str, str, tuple[str, ...], tuple[str, ...]], str] = {}
    for motif in selector_manifest.get("motifs", ()):
        if not isinstance(motif, Mapping):
            continue
        record = _review_motif(
            motif,
            validation=validations.get(str(motif.get("lane", ""))),
            visual=visual_records.get(str(motif.get("lane", ""))),
            hessian_lane=hessian_lanes.get(str(motif.get("lane", ""))),
        )
        record = _apply_duplicate_policy(record, seen_keys)
        reviewed_records.append(record)
        history.append(
            GRC9V3ReviewHistoryEntry(
                motif_id=record.motif_id,
                from_status=str(motif.get("review_status", "unreviewed")),
                to_status=record.review_status,
                reason=str(record.review_notes.get("review_reason", "")),
                reviewer=reviewer,
                timestamp_utc=review_timestamp_utc,
            )
        )
    return reviewed_records, history


def _review_motif(
    motif: Mapping[str, Any],
    *,
    validation: Mapping[str, Any] | None,
    visual: Mapping[str, Any] | None,
    hessian_lane: Mapping[str, Any] | None,
) -> GRC9V3ReviewedMotifRecord:
    lane_name = str(motif["lane"])
    notes = dict(motif.get("notes", {})) if isinstance(motif.get("notes"), Mapping) else {}
    event_sequence_delta = _event_sequence_delta(notes)
    missing_surface_fields = tuple(str(item) for item in motif.get("missing_surface_fields", ()))
    validation_missing_surfaces = tuple(
        str(item)
        for item in (validation or {}).get("missing_surface_selector_ids", ())
    )
    visual_artifacts = tuple(
        str(item) for item in (visual or {}).get("visual_artifacts", ())
    )
    checkpoint_links = tuple(
        dict(item)
        for item in (visual or {}).get("checkpoint_links", ())
        if isinstance(item, Mapping)
    )
    predicted = tuple(str(item) for item in motif.get("predicted_evidence_fields", ()))
    observed = tuple(str(item) for item in motif.get("observed_evidence_fields", ()))
    control_role = str(motif.get("control_role", notes.get("control_role", "")))
    confidence_score = int(motif.get("confidence_score", 0))
    hessian_classification = (
        "" if hessian_lane is None else str(hessian_lane.get("classification", ""))
    )
    has_lifecycle_evidence = any(
        fragment in field for field in (*predicted, *observed) for fragment in _LIFECYCLE_FIELD_FRAGMENTS
    )
    missing_surface = bool(missing_surface_fields or validation_missing_surfaces)
    if missing_surface:
        review_status = "needs-rerun"
        catalog_category = "needs_rerun"
        event_motif_eligible = False
        confidence_label = "needs-rerun"
        rejection_reason = "required telemetry surface was missing during selector validation"
        rerun_requested = True
        review_reason = "Required telemetry surface was missing."
    elif hessian_classification == "diagnostic_comparator":
        review_status = "diagnostic_comparator"
        catalog_category = "diagnostic_comparator"
        event_motif_eligible = False
        confidence_label = "diagnostic_comparator"
        rejection_reason = None
        rerun_requested = False
        review_reason = (
            "Hessian backend/tensor evidence is diagnostic; no lifecycle event "
            "delta was observed."
        )
    elif confidence_score >= 5 and control_role == "complex_control" and has_lifecycle_evidence:
        review_status = "accepted"
        catalog_category = "lifecycle_motif"
        event_motif_eligible = True
        confidence_label = "accepted_after_review"
        rejection_reason = None
        rerun_requested = False
        review_reason = (
            "Telemetry, selector, run-summary, and visual evidence support an "
            "eventful lifecycle motif."
        )
    elif confidence_score >= 5:
        review_status = "strong_candidate"
        catalog_category = (
            "negative_control" if control_role == "perturbation_control" else "strong_candidate"
        )
        event_motif_eligible = False
        confidence_label = "strong_candidate"
        rejection_reason = None
        rerun_requested = False
        review_reason = (
            "Selector evidence is strong, but this record is preserved as "
            "control or non-lifecycle evidence rather than accepted as an "
            "event motif."
        )
    else:
        review_status = "rejected"
        catalog_category = "rejected"
        event_motif_eligible = False
        confidence_label = "rejected"
        rejection_reason = "selector evidence did not satisfy review threshold"
        rerun_requested = False
        review_reason = str(rejection_reason)

    non_claims = list(_BASE_NON_CLAIMS)
    if review_status == "diagnostic_comparator":
        non_claims.append("no_hessian_lifecycle_motif_without_backend_event_delta")
    if catalog_category == "negative_control":
        non_claims.append("negative_control_not_promoted_to_event_motif")
    if event_sequence_delta:
        non_claims.append("composed_lane_has_recorded_lifecycle_side_effects")
    artifact_root = str(notes.get("artifact_root", ""))
    review_notes: dict[str, Any] = {
        "review_reason": review_reason,
        "visual_status": None if visual is None else visual.get("visual_status"),
        "overlay_status": None if visual is None else visual.get("overlay_status"),
        "selector_missing_ids": list((validation or {}).get("missing_selector_ids", ())),
        "hessian_classification": hessian_classification or None,
    }
    return GRC9V3ReviewedMotifRecord(
        motif_id=str(motif["motif_id"]),
        lane_name=lane_name,
        phenomenon=str(motif["phenomenon"]),
        profile=str(motif["profile"]),
        seed_name=str(motif["seed_name"]),
        run_id=str(motif["run_id"]),
        source_session_ids=tuple(str(item) for item in motif.get("session_ids", ())),
        step_window=_step_window(motif.get("step_window", (0, 0))),
        control_role=control_role,
        confidence_score=confidence_score,
        confidence_label=confidence_label,
        source_review_status=str(motif.get("review_status", "")),
        review_status=review_status,
        catalog_category=catalog_category,
        event_motif_eligible=event_motif_eligible,
        predicted_evidence_fields=predicted,
        observed_evidence_fields=observed,
        missing_surface_fields=(*missing_surface_fields, *validation_missing_surfaces),
        visual_artifacts=visual_artifacts,
        checkpoint_links=checkpoint_links,
        telemetry_artifact_root=artifact_root,
        event_sequence_delta=event_sequence_delta,
        non_claims=tuple(dict.fromkeys(non_claims)),
        rejection_reason=rejection_reason,
        rerun_requested=rerun_requested,
        review_notes=review_notes,
    )


def _apply_duplicate_policy(
    record: GRC9V3ReviewedMotifRecord,
    seen_keys: dict[tuple[str, str, tuple[str, ...], tuple[str, ...]], str],
) -> GRC9V3ReviewedMotifRecord:
    event_sequence = ()
    if record.event_sequence_delta:
        event_sequence = tuple(record.event_sequence_delta.get("observed", ()))
    key = (
        record.phenomenon,
        record.seed_name,
        tuple(record.predicted_evidence_fields),
        tuple(str(item) for item in event_sequence),
    )
    duplicate_of = seen_keys.get(key)
    if duplicate_of is None:
        seen_keys[key] = record.motif_id
        return record
    return GRC9V3ReviewedMotifRecord(
        **{
            **record.to_mapping(),
            "source_session_ids": tuple(record.source_session_ids),
            "step_window": tuple(record.step_window),
            "predicted_evidence_fields": tuple(record.predicted_evidence_fields),
            "observed_evidence_fields": tuple(record.observed_evidence_fields),
            "missing_surface_fields": tuple(record.missing_surface_fields),
            "visual_artifacts": tuple(record.visual_artifacts),
            "checkpoint_links": tuple(record.checkpoint_links),
            "non_claims": tuple(record.non_claims),
            "review_status": "duplicate",
            "catalog_category": "duplicate",
            "event_motif_eligible": False,
            "duplicate_of": duplicate_of,
            "review_notes": {
                **dict(record.review_notes or {}),
                "review_reason": f"Duplicate of reviewed motif {duplicate_of}.",
            },
        }
    )


def _event_sequence_delta(notes: Mapping[str, Any]) -> Mapping[str, Any] | None:
    raw = notes.get("event_sequence_delta")
    if not isinstance(raw, str) or not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"parse_error": raw}
    return parsed if isinstance(parsed, Mapping) else None


def _step_window(value: Any) -> tuple[int, int]:
    if isinstance(value, Sequence) and not isinstance(value, str) and len(value) >= 2:
        return (int(value[0]), int(value[1]))
    return (0, 0)


def _catalog_payload(session: GRC9V3ReviewedMotifCatalogSession) -> Mapping[str, Any]:
    return {
        "version": GRC9V3_REVIEWED_MOTIF_CATALOG_VERSION,
        "session_id": session.session_id,
        "selector_session_id": session.selector_session_id,
        "visual_session_id": session.visual_session_id,
        "hessian_review_session_id": session.hessian_review_session_id,
        "review_boundary": "visuals_are_secondary_and_hessian_backend_evidence_is_diagnostic_without_backend_event_delta",
        "records": [record.to_mapping() for record in session.records],
        "diagnostic_records": [dict(record) for record in session.diagnostic_records],
        "review_history": [entry.to_mapping() for entry in session.review_history],
        "summary": {
            key: value
            for key, value in session.to_mapping().items()
            if key.endswith("_count") or key.endswith("_counts")
        },
    }


def _session_manifest(session: GRC9V3ReviewedMotifCatalogSession) -> Mapping[str, Any]:
    return {
        "session_id": session.session_id,
        "program": "grc9v3_phenomenology_discovery",
        "family": "grc9v3",
        "track": "phenomenology_discovery",
        "iteration": "I09_reviewed_motif_catalog",
        "session_kind": "reviewed_motif_catalog",
        "phenomenon": "reviewed GRC9V3 runtime motif catalog",
        "seed_family": session.selector_session_id,
        "control_role": "catalog_review",
        "status": "completed",
        "created_at": "2026-04-26",
        "git_revision": _git_revision(),
        "dirty_worktree": None,
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_reviewed_motif_catalog --session-id {session.session_id}"
        ),
        "input_paths": [
            f"outputs/grc9v3/phenomenology_discovery/sessions/{session.selector_session_id}/selector_manifest.json",
            f"outputs/grc9v3/phenomenology_discovery/sessions/{session.selector_session_id}/reports/selector_validation_report.json",
            f"outputs/grc9v3/phenomenology_discovery/sessions/{session.visual_session_id}/visual_index.json",
            f"outputs/grc9v3/phenomenology_discovery/sessions/{session.hessian_review_session_id}/hessian_comparator_review.json",
        ],
        "output_paths": [
            session.reviewed_catalog_path,
            session.markdown_catalog_path,
            session.report_path,
        ],
        "prediction_summary": "Eventful complex candidates should promote to accepted motifs; Hessian comparators should remain diagnostic without backend event delta.",
        "observation_summary": (
            f"{session.to_mapping()['accepted_count']} accepted, "
            f"{session.to_mapping()['strong_candidate_count']} strong candidates, "
            f"{session.to_mapping()['diagnostic_comparator_count']} diagnostic comparators."
        ),
        "replay_notes": "Replay rebuilds the reviewed catalog from selector, visual, and Hessian review artifacts.",
    }


def _write_markdown_catalog(
    path: Path,
    session: GRC9V3ReviewedMotifCatalogSession,
) -> None:
    payload = session.to_mapping()
    lines = [
        "# GRC9V3 Reviewed Motif Catalog",
        "",
        f"Session: `{session.session_id}`",
        "",
        "## Summary",
        "",
        f"- Motifs: `{payload['motif_count']}`",
        f"- Accepted: `{payload['accepted_count']}`",
        f"- Strong candidates: `{payload['strong_candidate_count']}`",
        f"- Diagnostic comparators: `{payload['diagnostic_comparator_count']}`",
        f"- Rejected: `{payload['rejected_count']}`",
        f"- Needs rerun: `{payload['needs_rerun_count']}`",
        "",
        "## Records",
        "",
        "| Lane | Status | Category | Visuals | Checkpoints | Notes |",
        "|---|---|---|---:|---:|---|",
    ]
    for record in session.records:
        lines.append(
            "| "
            f"`{record.lane_name}` | `{record.review_status}` | "
            f"`{record.catalog_category}` | {len(record.visual_artifacts)} | "
            f"{len(record.checkpoint_links)} | "
            f"{record.review_notes.get('review_reason', '')} |"
        )
    lines.extend(["", "## Diagnostic Pair Records", ""])
    for diagnostic in session.diagnostic_records:
        lines.append(
            f"- `{diagnostic.get('pair_id', '')}`: "
            f"`{diagnostic.get('event_delta_status', '')}`, "
            f"action `{diagnostic.get('review_action', '')}`"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary_markdown(
    path: Path,
    session: GRC9V3ReviewedMotifCatalogSession,
) -> None:
    payload = session.to_mapping()
    lines = [
        f"# {session.session_id} Reviewed Motif Catalog Summary",
        "",
        f"- Motifs: `{payload['motif_count']}`",
        f"- Accepted: `{payload['accepted_count']}`",
        f"- Strong candidates: `{payload['strong_candidate_count']}`",
        f"- Diagnostic comparators: `{payload['diagnostic_comparator_count']}`",
        f"- Duplicates: `{payload['duplicate_count']}`",
        f"- Rejected: `{payload['rejected_count']}`",
        f"- Needs rerun: `{payload['needs_rerun_count']}`",
        f"- Review history entries: `{payload['review_history_count']}`",
        f"- Visual-linked records: `{payload['visual_linked_record_count']}`",
        f"- Checkpoint-linked records: `{payload['checkpoint_linked_record_count']}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_readme(root: Path, session: GRC9V3ReviewedMotifCatalogSession) -> None:
    root.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {session.session_id}. GRC9V3 Reviewed Motif Catalog",
        "",
        "Status: `completed`",
        "",
        "Replay:",
        "",
        "```bash",
        (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_reviewed_motif_catalog --session-id {session.session_id}"
        ),
        "```",
        "",
        "Primary artifacts:",
        "",
        "- `reviewed_motif_catalog.json`",
        "- `reviewed_motif_catalog.md`",
        "- `reports/reviewed_motif_catalog_report.json`",
        "- `reports/reviewed_motif_catalog_summary.md`",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _append_experimental_log(session: GRC9V3ReviewedMotifCatalogSession) -> None:
    EXPERIMENTAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not EXPERIMENTAL_LOG_PATH.exists():
        EXPERIMENTAL_LOG_PATH.write_text(_experimental_log_header(), encoding="utf-8")
    text = EXPERIMENTAL_LOG_PATH.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if not line.startswith(f"| `{session.session_id}` |")]
    payload = session.to_mapping()
    lines.append(
        f"| `{session.session_id}` | `completed` | `reviewed_motif_catalog` | "
        "`I09_reviewed_motif_catalog` | reviewed GRC9V3 runtime motif catalog | "
        f"`{session.selector_session_id}` | "
        f"`outputs/grc9v3/phenomenology_discovery/sessions/{session.session_id}/` | "
        f"Iteration 9: {payload['accepted_count']} accepted, "
        f"{payload['strong_candidate_count']} strong candidates, "
        f"{payload['diagnostic_comparator_count']} diagnostic comparators |"
    )
    EXPERIMENTAL_LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _experimental_log_header() -> str:
    return "\n".join(
        [
            "# GRC9V3 Phenomenology Discovery Experimental Log",
            "",
            "## Session Index",
            "",
            "| Session | Status | Kind | Iteration | Phenomenon | Seed Family | Artifact Root | Notes |",
            "|---|---|---|---|---|---|---|---|",
        ]
    ) + "\n"


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_required_json(path: Path, description: str) -> Mapping[str, Any]:
    if not path.exists():
        raise FileNotFoundError(2, f"{description} missing", str(path))
    return _read_json(path)


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_revision() -> str:
    try:
        result = subprocess.run(
            ("git", "rev-parse", "HEAD"),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", default="S0012")
    parser.add_argument("--selector-session-id", default="S0009")
    parser.add_argument("--visual-session-id", default="S0010")
    parser.add_argument("--hessian-review-session-id", default="S0011")
    parser.add_argument("--session-root", default=None)
    parser.add_argument("--full-json", action="store_true")
    args = parser.parse_args(argv)
    session = run_grc9v3_reviewed_motif_catalog(
        session_id=args.session_id,
        selector_session_id=args.selector_session_id,
        visual_session_id=args.visual_session_id,
        hessian_review_session_id=args.hessian_review_session_id,
        session_root=args.session_root,
    )
    payload = session.to_mapping()
    if args.full_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            {
                "session_id": session.session_id,
                "motif_count": payload["motif_count"],
                "accepted_count": payload["accepted_count"],
                "strong_candidate_count": payload["strong_candidate_count"],
                "diagnostic_comparator_count": payload["diagnostic_comparator_count"],
                "rejected_count": payload["rejected_count"],
                "needs_rerun_count": payload["needs_rerun_count"],
                "reviewed_catalog_path": session.reviewed_catalog_path,
                "markdown_catalog_path": session.markdown_catalog_path,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "GRC9V3_REVIEWED_MOTIF_CATALOG_VERSION",
    "GRC9V3ReviewHistoryEntry",
    "GRC9V3ReviewedMotifCatalogSession",
    "GRC9V3ReviewedMotifRecord",
    "run_grc9v3_reviewed_motif_catalog",
]
