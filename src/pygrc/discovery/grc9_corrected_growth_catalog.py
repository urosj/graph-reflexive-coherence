"""Corrected GRC9 growth catalog generation."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


GRC9_CORRECTED_GROWTH_CATALOG_VERSION = "grc9_corrected_growth_catalog_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9/phenomenology_discovery/sessions")
DEFAULT_CORRECTED_GRC9_SOURCE_SESSIONS = ("S0027", "S0029", "S0030")
DEFAULT_GROWTH_CLASSIFICATION_PATH = Path(
    "outputs/grcl9/lowering/sessions/S0034/growth_record_classification.json"
)


@dataclass(frozen=True)
class GRC9CorrectedGrowthCatalogSession:
    """Result from a corrected GRC9 growth catalog run."""

    session_id: str
    session_root: Path
    catalog_path: Path
    report_path: Path
    summary_path: Path
    accepted_growth_count: int
    accepted_control_count: int
    rejected_count: int
    supersession_link_count: int

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "session_root": str(self.session_root),
            "catalog_path": str(self.catalog_path),
            "report_path": str(self.report_path),
            "summary_path": str(self.summary_path),
            "accepted_growth_count": self.accepted_growth_count,
            "accepted_control_count": self.accepted_control_count,
            "rejected_count": self.rejected_count,
            "supersession_link_count": self.supersession_link_count,
        }


def run_grc9_corrected_growth_catalog(
    *,
    session_id: str = "S0035",
    source_session_ids: Sequence[str] = DEFAULT_CORRECTED_GRC9_SOURCE_SESSIONS,
    discovery_session_root: str | Path = DISCOVERY_SESSION_ROOT,
    growth_classification_path: str | Path = DEFAULT_GROWTH_CLASSIFICATION_PATH,
) -> GRC9CorrectedGrowthCatalogSession:
    """Publish a corrected GRC9 growth catalog from corrected discovery sessions."""

    if not session_id.startswith("S"):
        raise ValueError("session_id must be an S-prefixed discovery session id")
    if not source_session_ids:
        raise ValueError("source_session_ids must not be empty")

    root = Path(discovery_session_root)
    session_root = root / session_id
    reports_root = session_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    superseded = _load_superseded_grc9_records(Path(growth_classification_path))
    accepted_growth: list[dict[str, Any]] = []
    accepted_controls: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for source_session_id in source_session_ids:
        source_root = root / source_session_id
        for lane in _load_run_report_lanes(source_root):
            record = _review_lane(
                source_session_id=source_session_id,
                lane=lane,
                superseded=superseded,
            )
            if record["review_status"] == "accepted_corrected_growth":
                accepted_growth.append(record)
            elif record["review_status"] == "accepted_corrected_control":
                accepted_controls.append(record)
            else:
                rejected.append(record)

    catalog = _catalog_payload(
        session_id=session_id,
        session_root=session_root,
        source_session_ids=tuple(source_session_ids),
        growth_classification_path=Path(growth_classification_path),
        accepted_growth=accepted_growth,
        accepted_controls=accepted_controls,
        rejected=rejected,
    )
    report = _report_payload(catalog)

    catalog_path = session_root / "corrected_grc9_growth_catalog.json"
    report_path = reports_root / "corrected_grc9_growth_catalog_report.json"
    summary_path = reports_root / "corrected_grc9_growth_catalog_summary.md"
    _write_json(catalog_path, catalog)
    _write_json(report_path, report)
    _write_text(summary_path, _summary_markdown(catalog))
    _write_json(session_root / "session_manifest.json", _session_manifest(catalog))
    _write_readme(session_root, catalog)
    _append_experimental_log(root.parent / "ExperimentalLog.md", catalog)

    summary = catalog["summary"]
    return GRC9CorrectedGrowthCatalogSession(
        session_id=session_id,
        session_root=session_root,
        catalog_path=catalog_path,
        report_path=report_path,
        summary_path=summary_path,
        accepted_growth_count=int(summary["accepted_corrected_growth_count"]),
        accepted_control_count=int(summary["accepted_corrected_control_count"]),
        rejected_count=int(summary["rejected_count"]),
        supersession_link_count=int(summary["supersession_link_count"]),
    )


def review_corrected_grc9_growth_lane(
    *,
    source_session_id: str,
    lane: Mapping[str, Any],
    run_summary: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    superseded: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Review one corrected GRC9 lane for front-capacity growth acceptance."""

    lane_name = str(lane["lane_name"])
    artifact_root = Path(str(lane["artifact_root"]))
    grc9_ext = run_summary.get("family_extensions", {}).get("grc9", {})
    backend = grc9_ext.get("backend_summary", {})
    growth_summary = grc9_ext.get("growth_summary", {})
    lifecycle = grc9_ext.get("lifecycle_event_counts", {})
    growth_count = int(growth_summary.get("growth_count", lifecycle.get("growth_count", 0)) or 0)
    front_growth_count = int(growth_summary.get("front_capacity_growth_count", 0) or 0)
    legacy_growth_count = int(growth_summary.get("legacy_broad_growth_count", 0) or 0)
    mode = str(backend.get("growth_parent_eligibility_mode", ""))
    growth_events = [event for event in events if event.get("event_kind") == "growth"]
    event_evidence = [_growth_event_evidence(event) for event in growth_events]

    mode_ok = mode == "grc9_front_capacity"
    no_legacy = legacy_growth_count == 0
    event_count_ok = len(growth_events) == growth_count
    front_count_ok = front_growth_count == growth_count
    event_evidence_ok = all(
        evidence.get("parent_eligibility_mode") == "grc9_front_capacity"
        and evidence.get("front_growth_provenance_present") is True
        and evidence.get("legacy_broad_growth") is False
        for evidence in event_evidence
    )

    accepted_growth = (
        growth_count > 0
        and mode_ok
        and no_legacy
        and event_count_ok
        and front_count_ok
        and event_evidence_ok
    )
    accepted_control = growth_count == 0 and mode_ok and no_legacy
    review_status = (
        "accepted_corrected_growth"
        if accepted_growth
        else "accepted_corrected_control"
        if accepted_control
        else "rejected"
    )
    failure_reasons: list[str] = []
    if not mode_ok:
        failure_reasons.append("growth parent eligibility mode is not grc9_front_capacity")
    if not no_legacy:
        failure_reasons.append("legacy broad-growth count is nonzero")
    if growth_count > 0 and not front_count_ok:
        failure_reasons.append("front-capacity growth count does not match growth count")
    if growth_count > 0 and not event_count_ok:
        failure_reasons.append("growth event rows do not match run-summary growth count")
    if growth_count > 0 and not event_evidence_ok:
        failure_reasons.append("at least one growth event lacks front-capacity provenance")

    return {
        "motif_id": f"grc9-corrected-growth-{source_session_id.lower()}-{_slug(lane_name)}",
        "review_status": review_status,
        "family": "grc9",
        "source_session_id": source_session_id,
        "source_lane_name": lane_name,
        "seed_name": str(lane.get("seed_name", lane_name)),
        "profile": str(lane.get("profile", "")),
        "run_id": str(lane.get("run_id", run_summary.get("identity", {}).get("run_id", ""))),
        "requested_steps": int(lane.get("requested_steps", 0) or 0),
        "event_counts_by_kind": dict(lane.get("event_counts_by_kind", {})),
        "front_capacity_evidence": {
            "growth_parent_eligibility_mode": mode,
            "growth_count": growth_count,
            "front_capacity_growth_count": front_growth_count,
            "legacy_broad_growth_count": legacy_growth_count,
            "lowest_port_attachment_count": int(
                growth_summary.get("lowest_port_attachment_count", 0) or 0
            ),
            "growth_event_row_count": len(growth_events),
            "growth_event_evidence": event_evidence,
        },
        "supersedes_old_motif_ids": _superseded_ids_for_lane(
            lane_name=lane_name,
            growth_count=growth_count,
            superseded=superseded,
        ),
        "artifact_links": {
            "artifact_root": str(artifact_root),
            "run_summary": str(artifact_root / "telemetry" / "run_summary.json"),
            "events": str(artifact_root / "telemetry" / "events.jsonl"),
            "steps": str(artifact_root / "telemetry" / "steps.jsonl"),
            "graph_checkpoint_index": str(
                artifact_root / "telemetry" / "graph_checkpoints" / "index.json"
            ),
        },
        "failure_reasons": failure_reasons,
        "non_claims": [
            "grcl9_lowering",
            "grcv3_semantics",
            "lorentzian_causal_layer",
            "legacy_broad_growth_evidence",
        ],
    }


def _review_lane(
    *,
    source_session_id: str,
    lane: Mapping[str, Any],
    superseded: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    artifact_root = Path(str(lane["artifact_root"]))
    run_summary = _read_json(artifact_root / "telemetry" / "run_summary.json")
    events = _read_jsonl(artifact_root / "telemetry" / "events.jsonl")
    return review_corrected_grc9_growth_lane(
        source_session_id=source_session_id,
        lane=lane,
        run_summary=run_summary,
        events=events,
        superseded=superseded,
    )


def _load_run_report_lanes(source_root: Path) -> Sequence[Mapping[str, Any]]:
    report_path = source_root / "reports" / "run_report.json"
    report = _read_json(report_path)
    return tuple(item for item in report.get("lanes", ()) if isinstance(item, Mapping))


def _growth_event_evidence(event: Mapping[str, Any]) -> Mapping[str, Any]:
    grc9_ext = event.get("family_extensions", {}).get("grc9", {})
    evidence = grc9_ext.get("growth_evidence", {})
    if isinstance(evidence, Mapping):
        return {
            "parent_eligibility_mode": evidence.get("parent_eligibility_mode"),
            "parent_capacity_source": evidence.get("parent_capacity_source"),
            "front_growth_provenance_present": evidence.get(
                "front_growth_provenance_present"
            ),
            "legacy_broad_growth": evidence.get("legacy_broad_growth"),
            "selected_parent_port": evidence.get("selected_parent_port"),
            "birth_probability": evidence.get("birth_probability"),
        }
    return {}


def _load_superseded_grc9_records(classification_path: Path) -> Sequence[Mapping[str, Any]]:
    if not classification_path.exists():
        return ()
    classification = _read_json(classification_path)
    return tuple(
        record
        for record in classification.get("superseded_records", ())
        if isinstance(record, Mapping) and record.get("family") == "grc9"
    )


def _superseded_ids_for_lane(
    *,
    lane_name: str,
    growth_count: int,
    superseded: Sequence[Mapping[str, Any]],
) -> list[str]:
    if growth_count > 0:
        target = "growth_pressure_lambda_high"
    elif "zero_birth" in lane_name:
        target = "growth_pressure_lambda_low"
    else:
        return []
    ids: list[str] = []
    seen: set[str] = set()
    for record in superseded:
        if record.get("record_name") != target or not record.get("old_motif_id"):
            continue
        old_motif_id = str(record["old_motif_id"])
        if old_motif_id in seen:
            continue
        seen.add(old_motif_id)
        ids.append(old_motif_id)
    return ids


def _catalog_payload(
    *,
    session_id: str,
    session_root: Path,
    source_session_ids: Sequence[str],
    growth_classification_path: Path,
    accepted_growth: Sequence[Mapping[str, Any]],
    accepted_controls: Sequence[Mapping[str, Any]],
    rejected: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    all_records = [*accepted_growth, *accepted_controls, *rejected]
    source_counts = Counter(str(record["source_session_id"]) for record in all_records)
    supersession_link_count = sum(
        len(record.get("supersedes_old_motif_ids", ()))
        for record in [*accepted_growth, *accepted_controls]
    )
    return {
        "catalog_version": GRC9_CORRECTED_GROWTH_CATALOG_VERSION,
        "session_id": session_id,
        "session_root": str(session_root),
        "source_reference": "implementation/GRC9-GRCL9-GrowthCorrection-Plan.md",
        "source_session_ids": list(source_session_ids),
        "growth_classification_path": str(growth_classification_path),
        "review_policy": {
            "accepted_growth": (
                "growth_count > 0, growth_parent_eligibility_mode == "
                "grc9_front_capacity, no legacy broad growth, and every growth "
                "event row carries front-capacity provenance"
            ),
            "accepted_control": (
                "growth_count == 0 under grc9_front_capacity with no legacy "
                "broad-growth count"
            ),
        },
        "accepted_corrected_growth_motifs": list(accepted_growth),
        "accepted_corrected_control_motifs": list(accepted_controls),
        "rejected_motifs": list(rejected),
        "summary": {
            "accepted_corrected_growth_count": len(accepted_growth),
            "accepted_corrected_control_count": len(accepted_controls),
            "rejected_count": len(rejected),
            "supersession_link_count": supersession_link_count,
            "source_session_counts": dict(sorted(source_counts.items())),
            "accepted_legacy_broad_growth_count": sum(
                int(
                    record.get("front_capacity_evidence", {}).get(
                        "legacy_broad_growth_count", 0
                    )
                    or 0
                )
                for record in all_records
                if record.get("review_status")
                in {"accepted_corrected_growth", "accepted_corrected_control"}
            ),
        },
        "non_claims": [
            "corrected GRC9 growth catalog is native GRC9 evidence only",
            "GRCL-9 lowering evidence is published separately",
            "legacy broad-growth results remain replay-only diagnostics",
        ],
    }


def _report_payload(catalog: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "catalog_version": catalog["catalog_version"],
        "session_id": catalog["session_id"],
        "summary": catalog["summary"],
        "accepted_growth_motif_ids": [
            record["motif_id"] for record in catalog["accepted_corrected_growth_motifs"]
        ],
        "accepted_control_motif_ids": [
            record["motif_id"] for record in catalog["accepted_corrected_control_motifs"]
        ],
        "rejected_motif_ids": [
            record["motif_id"] for record in catalog["rejected_motifs"]
        ],
    }


def _session_manifest(catalog: Mapping[str, Any]) -> dict[str, Any]:
    session_id = str(catalog["session_id"])
    return {
        "session_id": session_id,
        "session_kind": "grc9_corrected_growth_catalog",
        "catalog_version": catalog["catalog_version"],
        "source_session_ids": catalog["source_session_ids"],
        "growth_classification_path": catalog["growth_classification_path"],
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9_corrected_growth_catalog --session-id {session_id}"
        ),
        "summary": catalog["summary"],
    }


def _summary_markdown(catalog: Mapping[str, Any]) -> str:
    summary = catalog["summary"]
    lines = [
        "# Corrected GRC9 Growth Catalog",
        "",
        f"- Session: `{catalog['session_id']}`",
        f"- Version: `{catalog['catalog_version']}`",
        f"- Accepted corrected growth motifs: {summary['accepted_corrected_growth_count']}",
        f"- Accepted corrected controls: {summary['accepted_corrected_control_count']}",
        f"- Rejected motifs: {summary['rejected_count']}",
        f"- Supersession links: {summary['supersession_link_count']}",
        f"- Accepted legacy broad-growth count: {summary['accepted_legacy_broad_growth_count']}",
        "",
        "## Accepted Growth",
        "",
    ]
    for record in catalog["accepted_corrected_growth_motifs"]:
        links = ", ".join(record.get("supersedes_old_motif_ids", ())) or "none"
        lines.append(
            f"- `{record['source_lane_name']}` from `{record['source_session_id']}` "
            f"supersedes: {links}"
        )
    lines.extend(["", "## Accepted Controls", ""])
    for record in catalog["accepted_corrected_control_motifs"]:
        links = ", ".join(record.get("supersedes_old_motif_ids", ())) or "none"
        lines.append(
            f"- `{record['source_lane_name']}` from `{record['source_session_id']}` "
            f"supersedes: {links}"
        )
    lines.append("")
    return "\n".join(lines)


def _write_readme(session_root: Path, catalog: Mapping[str, Any]) -> None:
    _write_text(
        session_root / "README.md",
        _summary_markdown(catalog)
        + "\nReplay:\n\n```bash\n"
        + _session_manifest(catalog)["replay_command"]
        + "\n```\n",
    )


def _append_experimental_log(path: Path, catalog: Mapping[str, Any]) -> None:
    entry = (
        f"\n## {catalog['session_id']} - Corrected GRC9 Growth Catalog\n\n"
        f"- Source sessions: {', '.join(catalog['source_session_ids'])}\n"
        f"- Accepted corrected growth motifs: "
        f"{catalog['summary']['accepted_corrected_growth_count']}\n"
        f"- Accepted corrected controls: "
        f"{catalog['summary']['accepted_corrected_control_count']}\n"
        f"- Supersession links: {catalog['summary']['supersession_link_count']}\n"
        f"- Artifact: `{catalog['session_root']}/corrected_grc9_growth_catalog.json`\n"
    )
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if f"## {catalog['session_id']} - Corrected GRC9 Growth Catalog" in text:
            return
        path.write_text(text.rstrip() + "\n" + entry, encoding="utf-8")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# GRC9 Phenomenology Discovery Experimental Log\n" + entry, encoding="utf-8")


def _slug(value: str) -> str:
    return value.replace("_", "-")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing GRC9 corrected catalog input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> tuple[dict[str, Any], ...]:
    if not path.exists():
        raise FileNotFoundError(f"missing GRC9 corrected catalog input: {path}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return tuple(rows)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish corrected GRC9 growth catalog.")
    parser.add_argument("--session-id", default="S0035")
    parser.add_argument("--discovery-session-root", default=str(DISCOVERY_SESSION_ROOT))
    parser.add_argument(
        "--growth-classification-path",
        default=str(DEFAULT_GROWTH_CLASSIFICATION_PATH),
    )
    parser.add_argument(
        "--source-session-id",
        action="append",
        dest="source_session_ids",
        help="Corrected GRC9 source session id. May be provided multiple times.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    session = run_grc9_corrected_growth_catalog(
        session_id=args.session_id,
        source_session_ids=tuple(args.source_session_ids or DEFAULT_CORRECTED_GRC9_SOURCE_SESSIONS),
        discovery_session_root=args.discovery_session_root,
        growth_classification_path=args.growth_classification_path,
    )
    print(json.dumps(session.to_mapping(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
