"""Catalog breadth expansion for GRC9V3 phenomenology discovery."""

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


GRC9V3_CATALOG_BREADTH_EXPANSION_VERSION = "grc9v3_catalog_breadth_expansion_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9v3/phenomenology_discovery/sessions")
EXPERIMENTAL_LOG_PATH = Path("outputs/grc9v3/phenomenology_discovery/ExperimentalLog.md")
_REVIEW_TIMESTAMP_UTC = "2026-04-26T00:00:00Z"
_REVIEWER = "phase_i09_1_breadth_policy"
_BASE_NON_CLAIMS = (
    "no_grcl9_source_lowering_claim",
    "no_lorentzian_causal_layer_claim",
    "no_visual_only_promotion",
)
_EVENTFUL_LIFECYCLE_KINDS = {
    "hybrid_spark_candidate",
    "hybrid_mechanical_expansion",
    "hybrid_spark_completed",
    "choice_detected",
    "collapse",
    "growth",
}
_DIAGNOSTIC_POSITIVE_PHENOMENA = {
    "budget_preservation",
    "transport_basin_rerouting",
    "coarse_cache_invalidation",
}


@dataclass(frozen=True)
class GRC9V3CatalogBreadthExpansionSession:
    session_id: str
    control_selector_session_id: str
    base_catalog_session_id: str
    records: tuple[Mapping[str, Any], ...]
    review_history: tuple[Mapping[str, Any], ...]
    expanded_catalog_path: str
    markdown_catalog_path: str
    report_path: str

    def to_mapping(self) -> Mapping[str, Any]:
        status_counts = Counter(str(record.get("review_status", "")) for record in self.records)
        category_counts = Counter(str(record.get("catalog_category", "")) for record in self.records)
        return {
            "session_id": self.session_id,
            "version": GRC9V3_CATALOG_BREADTH_EXPANSION_VERSION,
            "control_selector_session_id": self.control_selector_session_id,
            "base_catalog_session_id": self.base_catalog_session_id,
            "motif_count": len(self.records),
            "review_history_count": len(self.review_history),
            "review_status_counts": dict(sorted(status_counts.items())),
            "catalog_category_counts": dict(sorted(category_counts.items())),
            "accepted_count": status_counts.get("accepted", 0),
            "strong_candidate_count": status_counts.get("strong_candidate", 0),
            "diagnostic_comparator_count": status_counts.get("diagnostic_comparator", 0),
            "rejected_count": status_counts.get("rejected", 0),
            "duplicate_count": status_counts.get("duplicate", 0),
            "needs_rerun_count": status_counts.get("needs-rerun", 0),
            "simple_control_record_count": sum(
                1 for record in self.records if record.get("breadth_source") == "S0007"
            ),
            "base_catalog_record_count": sum(
                1 for record in self.records if record.get("breadth_source") == "S0012"
            ),
            "event_motif_eligible_count": sum(
                1 for record in self.records if bool(record.get("event_motif_eligible"))
            ),
            "records": [dict(record) for record in self.records],
            "review_history": [dict(item) for item in self.review_history],
            "expanded_catalog_path": self.expanded_catalog_path,
            "markdown_catalog_path": self.markdown_catalog_path,
            "report_path": self.report_path,
        }


def run_grc9v3_catalog_breadth_expansion(
    *,
    session_id: str = "S0013",
    control_selector_session_id: str = "S0007",
    base_catalog_session_id: str = "S0012",
    session_root: str | Path | None = None,
    control_selector_manifest_path: str | Path | None = None,
    control_selector_report_path: str | Path | None = None,
    base_catalog_path: str | Path | None = None,
    update_experimental_log: bool = True,
) -> GRC9V3CatalogBreadthExpansionSession:
    """Merge validated simple controls with the reviewed complex motif catalog."""

    for value in (session_id, control_selector_session_id, base_catalog_session_id):
        if not is_session_id(value):
            raise ValueError("session ids must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    selector_manifest = _read_required_json(
        Path(control_selector_manifest_path)
        if control_selector_manifest_path is not None
        else DISCOVERY_SESSION_ROOT / control_selector_session_id / "selector_manifest.json",
        "control selector manifest",
    )
    selector_report = _read_required_json(
        Path(control_selector_report_path)
        if control_selector_report_path is not None
        else DISCOVERY_SESSION_ROOT
        / control_selector_session_id
        / "reports"
        / "selector_validation_report.json",
        "control selector report",
    )
    base_catalog = _read_required_json(
        Path(base_catalog_path)
        if base_catalog_path is not None
        else DISCOVERY_SESSION_ROOT
        / base_catalog_session_id
        / "reviewed_motif_catalog.json",
        "base reviewed catalog",
    )
    records, history = _expanded_records(
        selector_manifest=selector_manifest,
        selector_report=selector_report,
        base_catalog=base_catalog,
    )
    expanded_catalog_path = root / "expanded_motif_catalog.json"
    markdown_catalog_path = root / "expanded_motif_catalog.md"
    report_path = reports_root / "catalog_breadth_expansion_report.json"
    session = GRC9V3CatalogBreadthExpansionSession(
        session_id=session_id,
        control_selector_session_id=control_selector_session_id,
        base_catalog_session_id=base_catalog_session_id,
        records=tuple(records),
        review_history=tuple(history),
        expanded_catalog_path=str(expanded_catalog_path),
        markdown_catalog_path=str(markdown_catalog_path),
        report_path=str(report_path),
    )
    _write_json(expanded_catalog_path, _catalog_payload(session))
    _write_markdown_catalog(markdown_catalog_path, session)
    _write_json(report_path, session.to_mapping())
    _write_json(root / "session_manifest.json", _session_manifest(session))
    _write_summary_markdown(reports_root / "catalog_breadth_expansion_summary.md", session)
    _write_readme(root, session)
    if update_experimental_log and session_root is None:
        _append_experimental_log(session)
    return session


def _expanded_records(
    *,
    selector_manifest: Mapping[str, Any],
    selector_report: Mapping[str, Any],
    base_catalog: Mapping[str, Any],
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    validations = {
        str(item.get("lane_name")): item
        for item in selector_report.get("validations", ())
        if isinstance(item, Mapping) and item.get("lane_name")
    }
    records: list[Mapping[str, Any]] = []
    history: list[Mapping[str, Any]] = []
    seen_lanes: set[str] = set()
    for motif in selector_manifest.get("motifs", ()):
        if not isinstance(motif, Mapping):
            continue
        lane_name = str(motif["lane"])
        record = _record_from_control_motif(
            motif,
            validations.get(lane_name, {}),
        )
        records.append(record)
        history.append(_history_entry(record, from_status=str(motif.get("review_status", ""))))
        seen_lanes.add(lane_name)
    for record in base_catalog.get("records", ()):
        if not isinstance(record, Mapping):
            continue
        lane_name = str(record.get("lane_name", ""))
        if lane_name in seen_lanes:
            continue
        copied = {
            **dict(record),
            "breadth_source": "S0012",
            "breadth_role": "complex_reviewed_catalog",
        }
        records.append(copied)
        history.append(_history_entry(copied, from_status=str(record.get("review_status", ""))))
    return records, history


def _record_from_control_motif(
    motif: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> Mapping[str, Any]:
    lane_name = str(motif["lane"])
    notes = dict(motif.get("notes", {})) if isinstance(motif.get("notes"), Mapping) else {}
    artifact_root = str(notes.get("artifact_root", ""))
    event_counts = {
        str(key): int(value)
        for key, value in dict(validation.get("event_counts_by_kind", {})).items()
    }
    review_status, category, eligible, reason = _classification(
        motif,
        validation,
        event_counts=event_counts,
    )
    missing_surface_fields = tuple(str(item) for item in motif.get("missing_surface_fields", ()))
    missing_surface_fields = (
        *missing_surface_fields,
        *tuple(str(item) for item in validation.get("missing_surface_selector_ids", ())),
    )
    non_claims = list(_BASE_NON_CLAIMS)
    if category in {"negative_control", "quiescent_control"}:
        non_claims.append("control_record_not_promoted_to_event_motif")
    if category in {"mechanism_diagnostic_motif", "diagnostic_comparator"}:
        non_claims.append("diagnostic_record_not_lifecycle_event_motif")
    return {
        "motif_id": str(motif["motif_id"]),
        "lane_name": lane_name,
        "phenomenon": str(motif["phenomenon"]),
        "profile": str(motif["profile"]),
        "seed_name": str(motif["seed_name"]),
        "run_id": str(motif["run_id"]),
        "source_session_ids": [str(item) for item in motif.get("session_ids", ())],
        "step_window": list(_step_window(motif.get("step_window", (0, 0)))),
        "control_role": str(motif.get("control_role", notes.get("control_role", ""))),
        "confidence_score": int(motif.get("confidence_score", 0)),
        "confidence_label": (
            "accepted_after_review"
            if review_status == "accepted"
            else review_status
        ),
        "source_review_status": str(motif.get("review_status", "")),
        "review_status": review_status,
        "catalog_category": category,
        "event_motif_eligible": eligible,
        "event_counts_by_kind": event_counts,
        "predicted_evidence_fields": [
            str(item) for item in motif.get("predicted_evidence_fields", ())
        ],
        "observed_evidence_fields": [
            str(item) for item in motif.get("observed_evidence_fields", ())
        ],
        "missing_surface_fields": list(missing_surface_fields),
        "visual_artifacts": [],
        "checkpoint_links": _checkpoint_links(artifact_root),
        "telemetry_artifact_root": artifact_root,
        "event_sequence_delta": None,
        "non_claims": list(dict.fromkeys(non_claims)),
        "rejection_reason": (
            None if review_status != "rejected" else "selector evidence did not pass"
        ),
        "rerun_requested": review_status == "needs-rerun",
        "duplicate_of": None,
        "review_notes": {
            "review_reason": reason,
            "selector_missing_ids": list(validation.get("missing_selector_ids", ())),
            "evidence_mode": notes.get("evidence_mode"),
            "expected_outcome": notes.get("expected_outcome"),
        },
        "breadth_source": "S0007",
        "breadth_role": "simple_control_selector_catalog",
    }


def _classification(
    motif: Mapping[str, Any],
    validation: Mapping[str, Any],
    *,
    event_counts: Mapping[str, int],
) -> tuple[str, str, bool, str]:
    if validation.get("missing_surface_selector_ids"):
        return (
            "needs-rerun",
            "needs_rerun",
            False,
            "Required selector telemetry surface was missing.",
        )
    if validation.get("missing_selector_ids"):
        return (
            "rejected",
            "rejected",
            False,
            "Selector expectations were not satisfied.",
        )
    control_role = str(motif.get("control_role", ""))
    phenomenon = str(motif.get("phenomenon", ""))
    eventful = any(count > 0 for kind, count in event_counts.items() if kind in _EVENTFUL_LIFECYCLE_KINDS)
    if phenomenon == "hessian_backend_comparison":
        return (
            "diagnostic_comparator",
            "diagnostic_comparator",
            False,
            "Hessian backend comparison is diagnostic unless it changes lifecycle outcome.",
        )
    if control_role == "no_event_control":
        return (
            "strong_candidate",
            "quiescent_control",
            False,
            "No-event control validates quiescent baseline behavior.",
        )
    if control_role == "negative_control":
        return (
            "strong_candidate",
            "negative_control",
            False,
            "Negative control evidence is preserved but not promoted to an event motif.",
        )
    if control_role == "positive_control" and eventful:
        return (
            "accepted",
            "simple_lifecycle_motif",
            True,
            "Positive simple-control lane has matching lifecycle telemetry evidence.",
        )
    if control_role == "positive_control" and phenomenon in _DIAGNOSTIC_POSITIVE_PHENOMENA:
        return (
            "accepted",
            "mechanism_diagnostic_motif",
            False,
            "Positive simple-control lane has matching mechanism-specific telemetry evidence.",
        )
    return (
        "strong_candidate",
        "strong_candidate",
        False,
        "Selector evidence is strong but not enough for accepted lifecycle or diagnostic status.",
    )


def _checkpoint_links(artifact_root: str) -> list[Mapping[str, Any]]:
    if not artifact_root:
        return []
    checkpoint_root = Path(artifact_root) / "telemetry" / "graph_checkpoints"
    index_path = checkpoint_root / "index.json"
    if not index_path.exists():
        return []
    index = _read_json(index_path)
    links = []
    for item in index.get("checkpoints", ()):
        if not isinstance(item, Mapping):
            continue
        links.append(
            {
                "checkpoint_id": str(item.get("checkpoint_id", "")),
                "step_index": int(item.get("step_index", 0)),
                "path": str(checkpoint_root / str(item.get("path", ""))),
                "event_counts_by_kind_window": dict(item.get("event_counts_by_kind_window", {})),
            }
        )
    return links


def _history_entry(record: Mapping[str, Any], *, from_status: str) -> Mapping[str, Any]:
    return {
        "motif_id": str(record.get("motif_id", "")),
        "from_status": from_status,
        "to_status": str(record.get("review_status", "")),
        "reason": str(dict(record.get("review_notes", {})).get("review_reason", "")),
        "reviewer": _REVIEWER,
        "timestamp_utc": _REVIEW_TIMESTAMP_UTC,
    }


def _step_window(value: Any) -> tuple[int, int]:
    if isinstance(value, Sequence) and not isinstance(value, str) and len(value) >= 2:
        return (int(value[0]), int(value[1]))
    return (0, 0)


def _catalog_payload(session: GRC9V3CatalogBreadthExpansionSession) -> Mapping[str, Any]:
    return {
        "version": GRC9V3_CATALOG_BREADTH_EXPANSION_VERSION,
        "session_id": session.session_id,
        "control_selector_session_id": session.control_selector_session_id,
        "base_catalog_session_id": session.base_catalog_session_id,
        "review_boundary": "breadth_expansion_preserves_simple_controls_without_weakening_complex_catalog_acceptance",
        "records": [dict(record) for record in session.records],
        "review_history": [dict(item) for item in session.review_history],
        "summary": {
            key: value
            for key, value in session.to_mapping().items()
            if key.endswith("_count") or key.endswith("_counts")
        },
    }


def _session_manifest(session: GRC9V3CatalogBreadthExpansionSession) -> Mapping[str, Any]:
    payload = session.to_mapping()
    return {
        "session_id": session.session_id,
        "program": "grc9v3_phenomenology_discovery",
        "family": "grc9v3",
        "track": "phenomenology_discovery",
        "iteration": "I09_1_catalog_breadth_expansion",
        "session_kind": "catalog_breadth_expansion",
        "phenomenon": "expanded GRC9V3 runtime motif catalog breadth",
        "seed_family": session.control_selector_session_id,
        "control_role": "catalog_breadth_review",
        "status": "completed",
        "created_at": "2026-04-26",
        "git_revision": _git_revision(),
        "dirty_worktree": None,
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_catalog_breadth_expansion --session-id {session.session_id}"
        ),
        "input_paths": [
            f"outputs/grc9v3/phenomenology_discovery/sessions/{session.control_selector_session_id}/selector_manifest.json",
            f"outputs/grc9v3/phenomenology_discovery/sessions/{session.control_selector_session_id}/reports/selector_validation_report.json",
            f"outputs/grc9v3/phenomenology_discovery/sessions/{session.base_catalog_session_id}/reviewed_motif_catalog.json",
        ],
        "output_paths": [
            session.expanded_catalog_path,
            session.markdown_catalog_path,
            session.report_path,
        ],
        "prediction_summary": "S0007 simple controls should expand catalog breadth while S0012 keeps complex reviewed evidence intact.",
        "observation_summary": (
            f"{payload['motif_count']} total records, {payload['accepted_count']} accepted, "
            f"{payload['strong_candidate_count']} strong candidates, "
            f"{payload['diagnostic_comparator_count']} diagnostic comparators."
        ),
        "replay_notes": "Replay rebuilds the expanded catalog from S0007 and S0012 artifacts.",
    }


def _write_markdown_catalog(
    path: Path,
    session: GRC9V3CatalogBreadthExpansionSession,
) -> None:
    payload = session.to_mapping()
    lines = [
        "# GRC9V3 Expanded Motif Catalog",
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
        f"- Simple-control records: `{payload['simple_control_record_count']}`",
        f"- Base catalog records: `{payload['base_catalog_record_count']}`",
        "",
        "## Records",
        "",
        "| Lane | Status | Category | Source | Checkpoints | Notes |",
        "|---|---|---|---|---:|---|",
    ]
    for record in session.records:
        notes = dict(record.get("review_notes", {}))
        lines.append(
            "| "
            f"`{record.get('lane_name')}` | `{record.get('review_status')}` | "
            f"`{record.get('catalog_category')}` | `{record.get('breadth_source')}` | "
            f"{len(record.get('checkpoint_links', ())) } | "
            f"{notes.get('review_reason', '')} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary_markdown(
    path: Path,
    session: GRC9V3CatalogBreadthExpansionSession,
) -> None:
    payload = session.to_mapping()
    lines = [
        f"# {session.session_id} Catalog Breadth Expansion Summary",
        "",
        f"- Motifs: `{payload['motif_count']}`",
        f"- Accepted: `{payload['accepted_count']}`",
        f"- Strong candidates: `{payload['strong_candidate_count']}`",
        f"- Diagnostic comparators: `{payload['diagnostic_comparator_count']}`",
        f"- Rejected: `{payload['rejected_count']}`",
        f"- Needs rerun: `{payload['needs_rerun_count']}`",
        f"- Simple-control records: `{payload['simple_control_record_count']}`",
        f"- Base catalog records: `{payload['base_catalog_record_count']}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_readme(root: Path, session: GRC9V3CatalogBreadthExpansionSession) -> None:
    root.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {session.session_id}. GRC9V3 Catalog Breadth Expansion",
        "",
        "Status: `completed`",
        "",
        "Replay:",
        "",
        "```bash",
        (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_catalog_breadth_expansion --session-id {session.session_id}"
        ),
        "```",
        "",
        "Primary artifacts:",
        "",
        "- `expanded_motif_catalog.json`",
        "- `expanded_motif_catalog.md`",
        "- `reports/catalog_breadth_expansion_report.json`",
        "- `reports/catalog_breadth_expansion_summary.md`",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _append_experimental_log(session: GRC9V3CatalogBreadthExpansionSession) -> None:
    EXPERIMENTAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not EXPERIMENTAL_LOG_PATH.exists():
        EXPERIMENTAL_LOG_PATH.write_text(_experimental_log_header(), encoding="utf-8")
    text = EXPERIMENTAL_LOG_PATH.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if not line.startswith(f"| `{session.session_id}` |")]
    payload = session.to_mapping()
    lines.append(
        f"| `{session.session_id}` | `completed` | `catalog_breadth_expansion` | "
        "`I09_1_catalog_breadth_expansion` | expanded GRC9V3 runtime motif catalog breadth | "
        f"`{session.control_selector_session_id}` | "
        f"`outputs/grc9v3/phenomenology_discovery/sessions/{session.session_id}/` | "
        f"Iteration 9.1: {payload['motif_count']} records, "
        f"{payload['accepted_count']} accepted, {payload['strong_candidate_count']} strong candidates, "
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
    parser.add_argument("--session-id", default="S0013")
    parser.add_argument("--control-selector-session-id", default="S0007")
    parser.add_argument("--base-catalog-session-id", default="S0012")
    parser.add_argument("--session-root", default=None)
    parser.add_argument("--full-json", action="store_true")
    args = parser.parse_args(argv)
    session = run_grc9v3_catalog_breadth_expansion(
        session_id=args.session_id,
        control_selector_session_id=args.control_selector_session_id,
        base_catalog_session_id=args.base_catalog_session_id,
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
                "expanded_catalog_path": session.expanded_catalog_path,
                "markdown_catalog_path": session.markdown_catalog_path,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "GRC9V3_CATALOG_BREADTH_EXPANSION_VERSION",
    "GRC9V3CatalogBreadthExpansionSession",
    "run_grc9v3_catalog_breadth_expansion",
]
