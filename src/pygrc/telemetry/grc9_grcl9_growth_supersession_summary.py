"""Supersession summary for the GRC9/GRCL-9 growth correction."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .grcl9_replay import GRCL9_REPLAY_ROOT


GROWTH_SUPERSESSION_SUMMARY_VERSION = "grc9_grcl9_growth_supersession_summary_v1"
DEFAULT_CLASSIFICATION_PATH = Path(
    "outputs/grcl9/lowering/sessions/S0034/growth_record_classification.json"
)
DEFAULT_GRC9_CATALOG_PATH = Path(
    "outputs/grc9/phenomenology_discovery/sessions/S0035/corrected_grc9_growth_catalog.json"
)
DEFAULT_GRCL9_CATALOG_PATH = Path(
    "outputs/grcl9/lowering/sessions/S0036/corrected_grcl9_growth_catalog.json"
)


@dataclass(frozen=True)
class GrowthSupersessionSummarySession:
    """Result from a growth-correction supersession summary run."""

    session_id: str
    session_root: Path
    summary_path: Path
    report_path: Path
    markdown_path: Path
    retained_non_growth_count: int
    superseded_count: int
    accepted_corrected_growth_count: int
    unresolved_superseded_count: int

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "session_root": str(self.session_root),
            "summary_path": str(self.summary_path),
            "report_path": str(self.report_path),
            "markdown_path": str(self.markdown_path),
            "retained_non_growth_count": self.retained_non_growth_count,
            "superseded_count": self.superseded_count,
            "accepted_corrected_growth_count": self.accepted_corrected_growth_count,
            "unresolved_superseded_count": self.unresolved_superseded_count,
        }


def run_growth_supersession_summary(
    *,
    session_id: str = "S0037",
    output_root: str | Path = GRCL9_REPLAY_ROOT,
    classification_path: str | Path = DEFAULT_CLASSIFICATION_PATH,
    grc9_catalog_path: str | Path = DEFAULT_GRC9_CATALOG_PATH,
    grcl9_catalog_path: str | Path = DEFAULT_GRCL9_CATALOG_PATH,
) -> GrowthSupersessionSummarySession:
    """Write the Iteration 6.4 migration summary."""

    if not session_id.startswith("S"):
        raise ValueError("session_id must be an S-prefixed session id")
    root = Path(output_root)
    session_root = root / "sessions" / session_id
    reports_root = session_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    classification = _read_json(Path(classification_path))
    grc9_catalog = _read_json(Path(grc9_catalog_path))
    grcl9_catalog = _read_json(Path(grcl9_catalog_path))
    payload = build_growth_supersession_summary(
        session_id=session_id,
        session_root=session_root,
        classification=classification,
        grc9_catalog=grc9_catalog,
        grcl9_catalog=grcl9_catalog,
        classification_path=Path(classification_path),
        grc9_catalog_path=Path(grc9_catalog_path),
        grcl9_catalog_path=Path(grcl9_catalog_path),
    )
    report = _report_payload(payload)

    summary_path = session_root / "growth_correction_supersession_summary.json"
    report_path = reports_root / "growth_correction_supersession_report.json"
    markdown_path = reports_root / "growth_correction_supersession_summary.md"
    _write_json(summary_path, payload)
    _write_json(report_path, report)
    _write_text(markdown_path, _summary_markdown(payload))
    _write_json(session_root / "session_manifest.json", _session_manifest(payload))
    _write_readme(session_root, payload)
    _append_experimental_log(root / "ExperimentalLog.md", payload)
    _append_experimental_log(_grc9_experimental_log_path(Path(grc9_catalog_path)), payload, grc9=True)

    summary = payload["summary"]
    return GrowthSupersessionSummarySession(
        session_id=session_id,
        session_root=session_root,
        summary_path=summary_path,
        report_path=report_path,
        markdown_path=markdown_path,
        retained_non_growth_count=int(summary["retained_non_growth_record_count"]),
        superseded_count=int(summary["superseded_record_count"]),
        accepted_corrected_growth_count=int(
            summary["accepted_corrected_growth_record_count"]
        ),
        unresolved_superseded_count=int(summary["unresolved_superseded_record_count"]),
    )


def build_growth_supersession_summary(
    *,
    session_id: str,
    session_root: Path,
    classification: Mapping[str, Any],
    grc9_catalog: Mapping[str, Any],
    grcl9_catalog: Mapping[str, Any],
    classification_path: Path,
    grc9_catalog_path: Path,
    grcl9_catalog_path: Path,
) -> dict[str, Any]:
    """Build a deterministic summary payload from migration artifacts."""

    superseded_records = tuple(classification.get("superseded_records", ()))
    retained_records = tuple(classification.get("retained_non_growth_records", ()))
    grc9_growth = tuple(grc9_catalog.get("accepted_corrected_growth_motifs", ()))
    grc9_controls = tuple(grc9_catalog.get("accepted_corrected_control_motifs", ()))
    grcl9_growth = tuple(grcl9_catalog.get("accepted_corrected_growth_motifs", ()))
    grcl9_controls = tuple(grcl9_catalog.get("accepted_corrected_control_motifs", ()))
    grc9_rejected = tuple(grc9_catalog.get("rejected_motifs", ()))
    grcl9_rejected = tuple(grcl9_catalog.get("rejected_motifs", ()))
    linked_old_ids = _linked_old_ids(
        (*grc9_growth, *grc9_controls, *grcl9_growth, *grcl9_controls)
    )
    unresolved = tuple(
        record
        for record in superseded_records
        if str(record.get("old_motif_id", "")) not in linked_old_ids
    )
    unique_superseded_old_ids = sorted(
        {str(record.get("old_motif_id", "")) for record in superseded_records if record.get("old_motif_id")}
    )
    accepted_legacy_count = int(
        grc9_catalog.get("summary", {}).get("accepted_legacy_broad_growth_count", 0)
        or 0
    ) + int(
        grcl9_catalog.get("summary", {}).get("accepted_legacy_broad_growth_count", 0)
        or 0
    )
    replay_commands = _replay_commands(
        classification_path=classification_path,
        grc9_catalog_path=grc9_catalog_path,
        grcl9_catalog_path=grcl9_catalog_path,
    )
    return {
        "summary_version": GROWTH_SUPERSESSION_SUMMARY_VERSION,
        "session_id": session_id,
        "session_root": str(session_root),
        "source_reference": "implementation/GRC9-GRCL9-GrowthCorrection-Plan.md",
        "input_artifacts": {
            "classification": str(classification_path),
            "corrected_grc9_catalog": str(grc9_catalog_path),
            "corrected_grcl9_catalog": str(grcl9_catalog_path),
        },
        "migration_boundary": {
            "legacy_status": (
                "legacy_any_inactive_port broad-growth artifacts are replay-only "
                "diagnostics and are not accepted growth evidence"
            ),
            "corrected_status": (
                "accepted growth evidence requires front-capacity parent eligibility "
                "and explicit GRC9/GRCL-9 provenance"
            ),
            "non_growth_status": (
                "historical non-growth records remain retained when they do not "
                "depend on broad-growth semantics"
            ),
        },
        "summary": {
            "retained_non_growth_record_count": len(retained_records),
            "superseded_record_count": len(superseded_records),
            "unique_superseded_old_motif_id_count": len(unique_superseded_old_ids),
            "accepted_corrected_growth_record_count": len(grc9_growth)
            + len(grcl9_growth),
            "accepted_corrected_control_record_count": len(grc9_controls)
            + len(grcl9_controls),
            "rejected_corrected_record_count": len(grc9_rejected) + len(grcl9_rejected),
            "unresolved_superseded_record_count": len(unresolved),
            "unresolved_unique_old_motif_id_count": len(
                {str(record.get("old_motif_id", "")) for record in unresolved}
            ),
            "accepted_legacy_broad_growth_record_count": accepted_legacy_count,
            "grc9_accepted_corrected_growth_count": len(grc9_growth),
            "grcl9_accepted_corrected_growth_count": len(grcl9_growth),
            "grc9_accepted_corrected_control_count": len(grc9_controls),
            "grcl9_accepted_corrected_control_count": len(grcl9_controls),
        },
        "linked_old_motif_ids": sorted(linked_old_ids),
        "unresolved_superseded_records": [
            _compact_superseded_record(record) for record in unresolved
        ],
        "replay_commands": replay_commands,
        "historical_replay_artifacts": {
            "classification_source_catalogs": [
                *classification.get("grc9_catalog_paths", ()),
                *classification.get("grcl9_catalog_paths", ()),
            ],
            "classification_session": classification.get("session_id"),
            "corrected_grc9_catalog_session": grc9_catalog.get("session_id"),
            "corrected_grcl9_catalog_session": grcl9_catalog.get("session_id"),
        },
        "non_claims": [
            "The summary does not rewrite historical outputs.",
            "Superseded records remain replayable but are not accepted growth evidence.",
            "Corrected GRC9 and GRCL-9 catalogs remain separate evidence surfaces.",
        ],
    }


def _linked_old_ids(records: Sequence[Mapping[str, Any]]) -> set[str]:
    linked: set[str] = set()
    for record in records:
        for old_id in record.get("supersedes_old_motif_ids", ()):
            linked.add(str(old_id))
    return linked


def _compact_superseded_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "family": str(record.get("family", "")),
        "old_motif_id": str(record.get("old_motif_id", "")),
        "record_name": str(record.get("record_name", "")),
        "catalog_session_id": str(record.get("catalog_session_id", "")),
        "classification_status": str(record.get("classification_status", "")),
    }


def _replay_commands(
    *,
    classification_path: Path,
    grc9_catalog_path: Path,
    grcl9_catalog_path: Path,
) -> dict[str, str]:
    commands = {}
    for key, path in {
        "classification": classification_path,
        "corrected_grc9_catalog": grc9_catalog_path,
        "corrected_grcl9_catalog": grcl9_catalog_path,
    }.items():
        manifest_path = path.parent / "session_manifest.json"
        if manifest_path.exists():
            manifest = _read_json(manifest_path)
            commands[key] = str(manifest.get("replay_command", ""))
    commands["supersession_summary"] = (
        "PYTHONPATH=src ./.venv/bin/python -m "
        "pygrc.telemetry.grc9_grcl9_growth_supersession_summary --session-id S0037"
    )
    return commands


def _report_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "summary_version": payload["summary_version"],
        "session_id": payload["session_id"],
        "summary": payload["summary"],
        "unresolved_superseded_records": payload["unresolved_superseded_records"],
        "replay_commands": payload["replay_commands"],
    }


def _session_manifest(payload: Mapping[str, Any]) -> dict[str, Any]:
    session_id = str(payload["session_id"])
    return {
        "session_id": session_id,
        "session_kind": "growth_correction_supersession_summary",
        "summary_version": payload["summary_version"],
        "input_artifacts": payload["input_artifacts"],
        "replay_command": payload["replay_commands"]["supersession_summary"],
        "summary": payload["summary"],
    }


def _summary_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Growth Correction Supersession Summary",
        "",
        f"- Session: `{payload['session_id']}`",
        f"- Version: `{payload['summary_version']}`",
        f"- Retained non-growth records: {summary['retained_non_growth_record_count']}",
        f"- Superseded broad-growth records: {summary['superseded_record_count']}",
        f"- Unique superseded old motif ids: {summary['unique_superseded_old_motif_id_count']}",
        f"- Accepted corrected growth records: {summary['accepted_corrected_growth_record_count']}",
        f"- Accepted corrected controls: {summary['accepted_corrected_control_record_count']}",
        f"- Rejected corrected records: {summary['rejected_corrected_record_count']}",
        f"- Unresolved superseded records: {summary['unresolved_superseded_record_count']}",
        f"- Accepted legacy broad-growth records: {summary['accepted_legacy_broad_growth_record_count']}",
        "",
        "## Migration Boundary",
        "",
        f"- Legacy: {payload['migration_boundary']['legacy_status']}",
        f"- Corrected: {payload['migration_boundary']['corrected_status']}",
        f"- Non-growth: {payload['migration_boundary']['non_growth_status']}",
        "",
        "## Replay Commands",
        "",
    ]
    for label, command in payload["replay_commands"].items():
        lines.append(f"- `{label}`: `{command}`")
    unresolved = payload["unresolved_superseded_records"]
    lines.extend(["", "## Unresolved Superseded Records", ""])
    if unresolved:
        for record in unresolved:
            lines.append(
                f"- `{record['family']}` `{record['old_motif_id']}` "
                f"({record['record_name']})"
            )
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def _write_readme(session_root: Path, payload: Mapping[str, Any]) -> None:
    _write_text(session_root / "README.md", _summary_markdown(payload))


def _append_experimental_log(
    path: Path,
    payload: Mapping[str, Any],
    *,
    grc9: bool = False,
) -> None:
    title = "GRC9 Growth Supersession Summary" if grc9 else "Growth Supersession Summary"
    entry = (
        f"\n## {payload['session_id']} - {title}\n\n"
        f"- Retained non-growth records: "
        f"{payload['summary']['retained_non_growth_record_count']}\n"
        f"- Superseded broad-growth records: "
        f"{payload['summary']['superseded_record_count']}\n"
        f"- Accepted corrected growth records: "
        f"{payload['summary']['accepted_corrected_growth_record_count']}\n"
        f"- Unresolved superseded records: "
        f"{payload['summary']['unresolved_superseded_record_count']}\n"
        f"- Artifact: `{payload['session_root']}/growth_correction_supersession_summary.json`\n"
    )
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if f"## {payload['session_id']} - {title}" in text:
            return
        path.write_text(text.rstrip() + "\n" + entry, encoding="utf-8")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Growth Correction Experimental Log\n" + entry, encoding="utf-8")


def _grc9_experimental_log_path(grc9_catalog_path: Path) -> Path:
    # Expected layout: .../phenomenology_discovery/sessions/S0035/catalog.json
    if len(grc9_catalog_path.parents) >= 3:
        return grc9_catalog_path.parents[2] / "ExperimentalLog.md"
    return Path("outputs/grc9/phenomenology_discovery/ExperimentalLog.md")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing growth supersession input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


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
    parser = argparse.ArgumentParser(
        description="Publish GRC9/GRCL-9 growth supersession summary."
    )
    parser.add_argument("--session-id", default="S0037")
    parser.add_argument("--output-root", default=str(GRCL9_REPLAY_ROOT))
    parser.add_argument("--classification-path", default=str(DEFAULT_CLASSIFICATION_PATH))
    parser.add_argument("--grc9-catalog-path", default=str(DEFAULT_GRC9_CATALOG_PATH))
    parser.add_argument("--grcl9-catalog-path", default=str(DEFAULT_GRCL9_CATALOG_PATH))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    session = run_growth_supersession_summary(
        session_id=args.session_id,
        output_root=args.output_root,
        classification_path=args.classification_path,
        grc9_catalog_path=args.grc9_catalog_path,
        grcl9_catalog_path=args.grcl9_catalog_path,
    )
    print(json.dumps(session.to_mapping(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
