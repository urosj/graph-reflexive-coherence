"""Reviewed motif catalog generation for GRC9 phenomenology discovery."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any

from .grc9_manifest import (
    GRC9DiscoveryManifest,
    GRC9EvidenceFields,
    GRC9MotifRecord,
    GRC9ReviewHistoryEntry,
    is_session_id,
)


GRC9_REVIEWED_MOTIF_CATALOG_VERSION = "grc9_reviewed_motif_catalog_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9/phenomenology_discovery/sessions")
_REVIEW_TIMESTAMP_UTC = "2026-04-25T00:00:00Z"
_REVIEWER = "phase_i08_review_policy"


@dataclass(frozen=True)
class GRC9ReviewedMotifCatalogSession:
    session_id: str
    selector_session_id: str
    selector_manifest_path: str
    selector_report_path: str
    reviewed_manifest_path: str
    catalog_path: str
    report_path: str
    manifest: GRC9DiscoveryManifest
    accepted_count: int
    strong_candidate_count: int
    rejected_count: int
    duplicate_count: int
    needs_rerun_count: int

    def to_mapping(self) -> Mapping[str, Any]:
        status_counts = Counter(motif.review_status for motif in self.manifest.motifs)
        return {
            "session_id": self.session_id,
            "selector_session_id": self.selector_session_id,
            "version": GRC9_REVIEWED_MOTIF_CATALOG_VERSION,
            "selector_manifest_path": self.selector_manifest_path,
            "selector_report_path": self.selector_report_path,
            "reviewed_manifest_path": self.reviewed_manifest_path,
            "catalog_path": self.catalog_path,
            "report_path": self.report_path,
            "motif_count": len(self.manifest.motifs),
            "review_history_count": len(self.manifest.review_history),
            "review_status_counts": dict(sorted(status_counts.items())),
            "accepted_count": self.accepted_count,
            "strong_candidate_count": self.strong_candidate_count,
            "rejected_count": self.rejected_count,
            "duplicate_count": self.duplicate_count,
            "needs_rerun_count": self.needs_rerun_count,
        }


def run_grc9_reviewed_motif_catalog(
    *,
    session_id: str = "S0025",
    selector_session_id: str = "S0022",
    session_root: str | Path | None = None,
    selector_manifest_path: str | Path | None = None,
    selector_report_path: str | Path | None = None,
    reviewer: str = _REVIEWER,
    review_timestamp_utc: str = _REVIEW_TIMESTAMP_UTC,
) -> GRC9ReviewedMotifCatalogSession:
    """Review selector candidates and emit a stable GRC9-native motif catalog."""

    if not is_session_id(session_id) or not is_session_id(selector_session_id):
        raise ValueError("session ids must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    manifest_path = (
        Path(selector_manifest_path)
        if selector_manifest_path is not None
        else DISCOVERY_SESSION_ROOT / selector_session_id / "selector_manifest.json"
    )
    report_path = (
        Path(selector_report_path)
        if selector_report_path is not None
        else DISCOVERY_SESSION_ROOT
        / selector_session_id
        / "reports"
        / "selector_validation_report.json"
    )
    source_manifest = GRC9DiscoveryManifest.from_mapping(
        _read_required_json(manifest_path, "selector manifest")
    )
    selector_report = _read_required_json(report_path, "selector validation report")
    reviewed_manifest = _review_manifest(
        source_manifest,
        selector_report,
        reviewer=reviewer,
        review_timestamp_utc=review_timestamp_utc,
    )

    reviewed_manifest_path = root / "reviewed_manifest.json"
    catalog_path = root / "reviewed_motif_catalog.json"
    review_report_path = reports_root / "reviewed_motif_catalog_report.json"
    session = _session_from_manifest(
        session_id=session_id,
        selector_session_id=selector_session_id,
        selector_manifest_path=manifest_path,
        selector_report_path=report_path,
        reviewed_manifest_path=reviewed_manifest_path,
        catalog_path=catalog_path,
        report_path=review_report_path,
        manifest=reviewed_manifest,
    )
    _write_json(reviewed_manifest_path, reviewed_manifest.to_mapping())
    _write_json(catalog_path, _catalog_payload(session))
    _write_json(review_report_path, session.to_mapping())
    _write_json(root / "session_manifest.json", _session_manifest(session))
    _write_summary_markdown(reports_root / "reviewed_motif_catalog_summary.md", session)
    _write_readme(root, session)
    return session


def _review_manifest(
    source_manifest: GRC9DiscoveryManifest,
    selector_report: Mapping[str, Any],
    *,
    reviewer: str = _REVIEWER,
    review_timestamp_utc: str = _REVIEW_TIMESTAMP_UTC,
) -> GRC9DiscoveryManifest:
    validations_by_lane = {
        str(validation["lane_name"]): validation
        for validation in selector_report.get("validations", ())
        if isinstance(validation, Mapping) and "lane_name" in validation
    }
    reviewed_motifs: list[GRC9MotifRecord] = []
    review_history: list[GRC9ReviewHistoryEntry] = []
    seen_keys: dict[tuple[str, str, tuple[str, ...]], str] = {}

    for motif in source_manifest.motifs:
        reviewed, entry = _review_existing_motif(
            motif,
            validations_by_lane.get(motif.lane),
            reviewer=reviewer,
            review_timestamp_utc=review_timestamp_utc,
        )
        reviewed, entry = _apply_duplicate_policy(
            reviewed,
            entry,
            seen_keys,
            reviewer=reviewer,
            review_timestamp_utc=review_timestamp_utc,
        )
        reviewed_motifs.append(reviewed)
        review_history.append(entry)

    motif_lanes = {motif.lane for motif in source_manifest.motifs}
    for validation in selector_report.get("validations", ()):
        if not isinstance(validation, Mapping):
            continue
        if str(validation.get("lane_name", "")) in motif_lanes:
            continue
        if str(validation.get("confidence_label", "")) != "rejected":
            continue
        rejected = _rejected_motif_from_validation(validation)
        reviewed_motifs.append(rejected)
        review_history.append(
            _history_entry(
                motif_id=rejected.motif_id,
                from_status="unreviewed",
                to_status=rejected.review_status,
                reason=str(rejected.rejection_reason or "selector validation rejected the lane"),
                reviewer=reviewer,
                review_timestamp_utc=review_timestamp_utc,
            )
        )

    return GRC9DiscoveryManifest(
        source_artifacts=source_manifest.source_artifacts,
        run_scope=source_manifest.run_scope,
        structure_hypotheses=source_manifest.structure_hypotheses,
        selectors=source_manifest.selectors,
        motifs=tuple(reviewed_motifs),
        review_history=tuple(review_history),
        output_roots={
            **dict(source_manifest.output_roots or {}),
            "reviewed_catalog": "outputs/grc9/phenomenology_discovery",
        },
    )


def _review_existing_motif(
    motif: GRC9MotifRecord,
    validation: Mapping[str, Any] | None,
    *,
    reviewer: str,
    review_timestamp_utc: str,
) -> tuple[GRC9MotifRecord, GRC9ReviewHistoryEntry]:
    motif = _replace_motif(motif, notes=_notes_with_seed_metadata(motif))
    missing_surface = _has_missing_surface(validation)
    if missing_surface:
        reviewed = _replace_motif(
            motif,
            review_status="needs-rerun",
            confidence_label="needs-rerun",
            rerun_requested=True,
            rejection_reason="required telemetry surface was missing during selector validation",
        )
        return reviewed, _history_entry(
            motif_id=motif.motif_id,
            from_status=motif.review_status,
            to_status="needs-rerun",
            reason="Required telemetry surface was missing during selector validation.",
            reviewer=reviewer,
            review_timestamp_utc=review_timestamp_utc,
        )
    if motif.confidence_score >= 5:
        reviewed = _replace_motif(
            motif,
            review_status="accepted",
            confidence_label="accepted_after_review",
        )
        return reviewed, _history_entry(
            motif_id=motif.motif_id,
            from_status=motif.review_status,
            to_status="accepted",
            reason=(
                "Score 5 selector evidence includes clean perturbation/control "
                "separation and is promoted to accepted."
            ),
            reviewer=reviewer,
            review_timestamp_utc=review_timestamp_utc,
        )
    if motif.confidence_score >= 4:
        reviewed = _replace_motif(
            motif,
            review_status="strong_candidate",
            confidence_label="strong_candidate",
        )
        return reviewed, _history_entry(
            motif_id=motif.motif_id,
            from_status=motif.review_status,
            to_status="strong_candidate",
            reason="Score 4 telemetry, event, run-summary, and checkpoint evidence agree.",
            reviewer=reviewer,
            review_timestamp_utc=review_timestamp_utc,
        )
    if motif.confidence_score >= 2:
        reviewed = _replace_motif(motif, review_status="weak_candidate")
        return reviewed, _history_entry(
            motif_id=motif.motif_id,
            from_status=motif.review_status,
            to_status="weak_candidate",
            reason="Partial selector evidence remains useful but is not accepted.",
            reviewer=reviewer,
            review_timestamp_utc=review_timestamp_utc,
        )
    reviewed = _replace_motif(
        motif,
        review_status="rejected",
        confidence_label="rejected",
        rejection_reason="selector evidence contradicted the predicted signature",
    )
    return reviewed, _history_entry(
        motif_id=motif.motif_id,
        from_status=motif.review_status,
        to_status="rejected",
        reason=str(reviewed.rejection_reason),
        reviewer=reviewer,
        review_timestamp_utc=review_timestamp_utc,
    )


def _apply_duplicate_policy(
    motif: GRC9MotifRecord,
    entry: GRC9ReviewHistoryEntry,
    seen_keys: dict[tuple[str, str, tuple[str, ...]], str],
    *,
    reviewer: str,
    review_timestamp_utc: str,
) -> tuple[GRC9MotifRecord, GRC9ReviewHistoryEntry]:
    # Structural-signature dedupe: repeated artifacts of the same seed and
    # predicted field family collapse here, while distinct seed names remain separate.
    key = (motif.phenomenon, motif.seed_name, tuple(motif.predicted_evidence_fields))
    original_id = seen_keys.get(key)
    if original_id is None:
        seen_keys[key] = motif.motif_id
        return motif, entry
    reviewed = _replace_motif(
        motif,
        review_status="duplicate",
        confidence_label="rejected",
        rejection_reason=f"duplicate of {original_id}",
        notes={**dict(motif.notes or {}), "duplicate_of": original_id},
    )
    return reviewed, _history_entry(
        motif_id=motif.motif_id,
        from_status=entry.to_status,
        to_status="duplicate",
        reason=f"Duplicate structural signature already represented by {original_id}.",
        reviewer=reviewer,
        review_timestamp_utc=review_timestamp_utc,
    )


def _rejected_motif_from_validation(validation: Mapping[str, Any]) -> GRC9MotifRecord:
    lane_name = str(validation["lane_name"])
    session_id = str(validation["session_id"])
    missing_selector_ids = tuple(str(item) for item in validation.get("missing_selector_ids", ()))
    selector_results = tuple(
        item for item in validation.get("selector_results", ()) if isinstance(item, Mapping)
    )
    predicted_fields = tuple(str(item.get("field_path", "")) for item in selector_results)
    observed_fields = tuple(
        str(item.get("field_path", ""))
        for item in selector_results
        if bool(item.get("passed", False))
    )
    missing_fields = tuple(
        str(item.get("field_path", ""))
        for item in selector_results
        if not bool(item.get("passed", False))
    )
    requested_steps = int(validation.get("requested_steps", 0))
    return GRC9MotifRecord(
        motif_id=f"grc9-rejected-{session_id.lower()}-{lane_name.replace('_', '-')}",
        hypothesis_id=f"grc9_selector_{lane_name}",
        phenomenon=_phenomenon_for_lane(lane_name),
        profile=str(validation["profile"]),
        lane=lane_name,
        run_id=str(validation.get("run_id", "")),
        seed_name=str(validation.get("seed_name", lane_name)),
        session_ids=(session_id,),
        step_window=(0, requested_steps),
        checkpoint_ids=tuple(f"step-{step_index:08d}" for step_index in range(requested_steps + 1)),
        predicted_evidence_fields=predicted_fields,
        observed_evidence_fields=observed_fields,
        evidence_fields=GRC9EvidenceFields(
            predicted=predicted_fields,
            observed=observed_fields,
            missing=missing_fields,
        ),
        confidence_score=int(validation.get("confidence_score", 1)),
        confidence_label="rejected",
        review_status="rejected",
        rejection_reason=(
            "missing selector ids: " + ", ".join(missing_selector_ids)
            if missing_selector_ids
            else "selector validation rejected the lane"
        ),
        non_claims=(
            "grcv3_semantics",
            "grcl9_lowering",
            "lorentzian_causal_layer",
        ),
        notes={
            **{
                str(key): str(value)
                for key, value in dict(validation.get("notes", {})).items()
            },
            "review_source": "selector_validation_rejected_lane",
        },
    )


def _replace_motif(motif: GRC9MotifRecord, **updates: Any) -> GRC9MotifRecord:
    payload = dict(motif.to_mapping())
    payload.update(updates)
    return GRC9MotifRecord.from_mapping(payload)


def _notes_with_seed_metadata(motif: GRC9MotifRecord) -> Mapping[str, str]:
    notes = {str(key): str(value) for key, value in dict(motif.notes or {}).items()}
    artifact_root = notes.get("artifact_root")
    if not artifact_root:
        return notes
    run_summary_path = Path(artifact_root) / "telemetry" / "run_summary.json"
    notes.setdefault("seed_parameters_path", f"{run_summary_path}#raw_params")
    notes.setdefault(
        "runtime_parameter_overrides_path",
        f"{run_summary_path}#parameter_overrides",
    )
    notes.setdefault(
        "checkpoint_index_path",
        f"{Path(artifact_root) / 'telemetry' / 'graph_checkpoints' / 'index.json'}",
    )
    if not run_summary_path.exists():
        return notes
    try:
        run_summary = json.loads(run_summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return notes
    discovery = (
        run_summary.get("family_extensions", {})
        .get("discovery", {})
    )
    if isinstance(discovery, Mapping) and discovery.get("seed_family"):
        notes.setdefault("seed_family", str(discovery["seed_family"]))
    identity = run_summary.get("identity", {})
    if isinstance(identity, Mapping) and identity.get("seed_source_reference"):
        notes.setdefault("seed_source_reference", str(identity["seed_source_reference"]))
    return notes


def _has_missing_surface(validation: Mapping[str, Any] | None) -> bool:
    if validation is None:
        return False
    for result in validation.get("selector_results", ()):
        if not isinstance(result, Mapping):
            continue
        if str(result.get("observed_value", "")) == "missing_surface":
            return True
    return False


def _history_entry(
    *,
    motif_id: str,
    from_status: str,
    to_status: str,
    reason: str,
    reviewer: str,
    review_timestamp_utc: str,
) -> GRC9ReviewHistoryEntry:
    return GRC9ReviewHistoryEntry(
        motif_id=motif_id,
        from_status=from_status,
        to_status=to_status,
        reviewer=reviewer,
        reason=reason,
        timestamp_utc=review_timestamp_utc,
    )


def _phenomenon_for_lane(lane_name: str) -> str:
    if "fission" in lane_name and "growth" in lane_name and "spark" in lane_name:
        return "spark_growth_fission"
    if "fission" in lane_name and "spark" in lane_name:
        return "spark_fission"
    if "fission" in lane_name and "growth" in lane_name:
        return "growth_fission"
    if "growth" in lane_name and "spark" in lane_name:
        return "spark_growth"
    if "dual_spark" in lane_name:
        return "dual_spark"
    if "fission" in lane_name:
        return "fission"
    if "growth" in lane_name:
        return "growth"
    if "expansion" in lane_name or "d_eff" in lane_name:
        return "expansion"
    if "spark" in lane_name:
        return "spark"
    return "diagnostic"


def _session_from_manifest(
    *,
    session_id: str,
    selector_session_id: str,
    selector_manifest_path: Path,
    selector_report_path: Path,
    reviewed_manifest_path: Path,
    catalog_path: Path,
    report_path: Path,
    manifest: GRC9DiscoveryManifest,
) -> GRC9ReviewedMotifCatalogSession:
    counts = Counter(motif.review_status for motif in manifest.motifs)
    return GRC9ReviewedMotifCatalogSession(
        session_id=session_id,
        selector_session_id=selector_session_id,
        selector_manifest_path=str(selector_manifest_path),
        selector_report_path=str(selector_report_path),
        reviewed_manifest_path=str(reviewed_manifest_path),
        catalog_path=str(catalog_path),
        report_path=str(report_path),
        manifest=manifest,
        accepted_count=counts.get("accepted", 0),
        strong_candidate_count=counts.get("strong_candidate", 0),
        rejected_count=counts.get("rejected", 0),
        duplicate_count=counts.get("duplicate", 0),
        needs_rerun_count=counts.get("needs-rerun", 0),
    )


def _catalog_payload(session: GRC9ReviewedMotifCatalogSession) -> Mapping[str, Any]:
    accepted = tuple(
        motif for motif in session.manifest.motifs if motif.review_status == "accepted"
    )
    return {
        "version": GRC9_REVIEWED_MOTIF_CATALOG_VERSION,
        "session_id": session.session_id,
        "selector_session_id": session.selector_session_id,
        "accepted_count": len(accepted),
        "accepted_motifs": [motif.to_mapping() for motif in accepted],
        "review_status_counts": session.to_mapping()["review_status_counts"],
        "non_claims": sorted(
            {claim for motif in session.manifest.motifs for claim in motif.non_claims}
        ),
    }


def _session_manifest(session: GRC9ReviewedMotifCatalogSession) -> Mapping[str, Any]:
    return {
        "session_id": session.session_id,
        "program": "grc9_phenomenology_discovery",
        "family": "grc9",
        "track": "phenomenology_discovery",
        "iteration": "I08_reviewed_motif_catalog",
        "session_kind": "reviewed_motif_catalog",
        "phenomenon": "reviewed grc9-native motifs",
        "seed_family": session.selector_session_id,
        "control_role": "review",
        "status": "completed",
        "created_at": "2026-04-25",
        "git_revision": _git_revision(),
        "dirty_worktree": None,
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9_reviewed_motif_catalog --session-id {session.session_id} "
            f"--selector-session-id {session.selector_session_id}"
        ),
        "input_paths": [
            session.selector_manifest_path,
            session.selector_report_path,
        ],
        "output_paths": [
            session.reviewed_manifest_path,
            session.catalog_path,
            session.report_path,
        ],
        "observation_summary": (
            f"Reviewed {len(session.manifest.motifs)} motifs: "
            f"{session.accepted_count} accepted, "
            f"{session.strong_candidate_count} strong candidates, "
            f"{session.rejected_count} rejected."
        ),
    }


def _write_summary_markdown(path: Path, session: GRC9ReviewedMotifCatalogSession) -> None:
    payload = session.to_mapping()
    lines = [
        f"# {session.session_id} Reviewed Motif Catalog Summary",
        "",
        "## Scope",
        "",
        f"- Selector session: `{session.selector_session_id}`",
        f"- Motifs reviewed: `{payload['motif_count']}`",
        f"- Review history entries: `{payload['review_history_count']}`",
        f"- Review status counts: `{payload['review_status_counts']}`",
        "",
        "## Accepted Motifs",
        "",
    ]
    for motif in session.manifest.motifs:
        if motif.review_status != "accepted":
            continue
        lines.append(
            f"- `{motif.motif_id}`: `{motif.lane}`, score `{motif.confidence_score}`"
        )
    lines.extend(["", "## Rejected Motifs", ""])
    for motif in session.manifest.motifs:
        if motif.review_status != "rejected":
            continue
        lines.append(f"- `{motif.motif_id}`: {motif.rejection_reason}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_readme(root: Path, session: GRC9ReviewedMotifCatalogSession) -> None:
    lines = [
        f"# {session.session_id}. GRC9 Reviewed Motif Catalog",
        "",
        "Status: `completed`",
        "",
        "Replay:",
        "",
        "```bash",
        (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9_reviewed_motif_catalog --session-id {session.session_id} "
            f"--selector-session-id {session.selector_session_id}"
        ),
        "```",
        "",
        "Primary artifacts:",
        "",
        "- `reviewed_manifest.json`",
        "- `reviewed_motif_catalog.json`",
        "- `reports/reviewed_motif_catalog_report.json`",
        "- `reports/reviewed_motif_catalog_summary.md`",
    ]
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _read_required_json(path: Path, description: str) -> Mapping[str, Any]:
    if not path.exists():
        raise FileNotFoundError(2, f"{description} missing", str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
    parser.add_argument("--session-id", default="S0025")
    parser.add_argument("--selector-session-id", default="S0022")
    parser.add_argument("--session-root", default=None)
    parser.add_argument("--selector-manifest-path", default=None)
    parser.add_argument("--selector-report-path", default=None)
    parser.add_argument("--reviewer", default=_REVIEWER)
    parser.add_argument("--review-timestamp-utc", default=_REVIEW_TIMESTAMP_UTC)
    parser.add_argument("--full-json", action="store_true")
    args = parser.parse_args(argv)
    session = run_grc9_reviewed_motif_catalog(
        session_id=args.session_id,
        selector_session_id=args.selector_session_id,
        session_root=args.session_root,
        selector_manifest_path=args.selector_manifest_path,
        selector_report_path=args.selector_report_path,
        reviewer=args.reviewer,
        review_timestamp_utc=args.review_timestamp_utc,
    )
    payload = session.to_mapping()
    if args.full_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            {
                "session_id": session.session_id,
                "selector_session_id": session.selector_session_id,
                "motif_count": payload["motif_count"],
                "review_status_counts": payload["review_status_counts"],
                "catalog_path": session.catalog_path,
                "report_path": session.report_path,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "GRC9_REVIEWED_MOTIF_CATALOG_VERSION",
    "GRC9ReviewedMotifCatalogSession",
    "run_grc9_reviewed_motif_catalog",
]
