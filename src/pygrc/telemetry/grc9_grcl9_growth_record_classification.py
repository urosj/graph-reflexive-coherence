"""Classify reviewed GRC9/GRCL-9 records affected by growth correction."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .grcl9_replay import GRCL9_REPLAY_ROOT


GROWTH_RECORD_CLASSIFICATION_VERSION = "grc9_grcl9_growth_record_classification_v1"
GRC9_REVIEWED_CATALOG_PATHS = (
    Path("outputs/grc9/phenomenology_discovery/sessions/S0018/reviewed_motif_catalog.json"),
    Path("outputs/grc9/phenomenology_discovery/sessions/S0025/reviewed_motif_catalog.json"),
)
GRCL9_REVIEWED_CATALOG_PATHS = (
    Path("outputs/grcl9/lowering/sessions/S0008/reviewed_grcl9_lowered_motif_catalog.json"),
    Path("outputs/grcl9/lowering/sessions/S0025/reviewed_grcl9_lowered_motif_catalog.json"),
)
DEFAULT_CORRECTED_SELECTOR_MANIFEST_PATH = (
    Path("outputs/grcl9/lowering/sessions/S0033/selector_manifest.json")
)
SUPERSEDED_STATUS = "superseded_by_growth_semantics_correction"
RETAINED_STATUS = "retained_non_growth"


@dataclass(frozen=True)
class GrowthRecordClassificationSession:
    """Result from an affected-record classification pass."""

    session_id: str
    session_root: Path
    classification_path: Path
    report_path: Path
    summary_path: Path
    reviewed_record_count: int
    retained_non_growth_count: int
    superseded_count: int

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "session_root": str(self.session_root),
            "classification_path": str(self.classification_path),
            "report_path": str(self.report_path),
            "summary_path": str(self.summary_path),
            "reviewed_record_count": self.reviewed_record_count,
            "retained_non_growth_count": self.retained_non_growth_count,
            "superseded_count": self.superseded_count,
        }


def run_growth_record_classification(
    *,
    session_id: str = "S0034",
    output_root: str | Path = GRCL9_REPLAY_ROOT,
    grc9_catalog_paths: Sequence[str | Path] = GRC9_REVIEWED_CATALOG_PATHS,
    grcl9_catalog_paths: Sequence[str | Path] = GRCL9_REVIEWED_CATALOG_PATHS,
    corrected_selector_manifest_path: str | Path | None = DEFAULT_CORRECTED_SELECTOR_MANIFEST_PATH,
) -> GrowthRecordClassificationSession:
    """Classify historical reviewed records against corrected growth semantics."""

    if not session_id.startswith("S"):
        raise ValueError("session_id must be an S-prefixed session id")
    root = Path(output_root)
    session_root = root / "sessions" / session_id
    reports_root = session_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    replacement_candidates = _load_replacement_candidates(corrected_selector_manifest_path)
    records = _classify_catalog_records(
        family="grc9",
        catalog_paths=tuple(Path(path) for path in grc9_catalog_paths),
        replacement_candidates=replacement_candidates,
    )
    records.extend(
        _classify_catalog_records(
            family="grcl9",
            catalog_paths=tuple(Path(path) for path in grcl9_catalog_paths),
            replacement_candidates=replacement_candidates,
        )
    )
    payload = _classification_payload(
        session_id=session_id,
        session_root=session_root,
        records=records,
        grc9_catalog_paths=tuple(Path(path) for path in grc9_catalog_paths),
        grcl9_catalog_paths=tuple(Path(path) for path in grcl9_catalog_paths),
        corrected_selector_manifest_path=(
            Path(corrected_selector_manifest_path)
            if corrected_selector_manifest_path is not None
            else None
        ),
    )
    report = _report_payload(payload)

    classification_path = session_root / "growth_record_classification.json"
    report_path = reports_root / "growth_record_classification_report.json"
    summary_path = reports_root / "growth_record_classification_summary.md"
    _write_json(classification_path, payload)
    _write_json(report_path, report)
    _write_text(summary_path, _summary_markdown(payload))
    _write_json(session_root / "session_manifest.json", _session_manifest(payload))
    _append_experimental_log(root / "ExperimentalLog.md", payload)

    summary = payload["summary"]
    return GrowthRecordClassificationSession(
        session_id=session_id,
        session_root=session_root,
        classification_path=classification_path,
        report_path=report_path,
        summary_path=summary_path,
        reviewed_record_count=int(summary["reviewed_record_count"]),
        retained_non_growth_count=int(summary["retained_non_growth_count"]),
        superseded_count=int(summary["superseded_count"]),
    )


def classify_reviewed_record(
    *,
    family: str,
    catalog_path: str | Path,
    catalog_session_id: str,
    record: Mapping[str, Any],
    replacement_candidates: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Return the growth-correction classification for one reviewed record."""

    name = _record_name(record)
    growth_dependent = _is_growth_dependent_record(record)
    status = SUPERSEDED_STATUS if growth_dependent else RETAINED_STATUS
    replacement_records = tuple(
        dict(item)
        for item in (replacement_candidates or {}).get(_replacement_key(name), ())
    )
    supersession_link = None
    if growth_dependent:
        supersession_link = {
            "old_motif_id": str(record.get("motif_id", "")),
            "supersession_status": SUPERSEDED_STATUS,
            "replacement_status": (
                "candidate_corrected_records_found"
                if replacement_records
                else "pending_corrected_catalog_mapping"
            ),
            "replacement_candidates": replacement_records,
        }
    return {
        "family": family,
        "catalog_path": str(catalog_path),
        "catalog_session_id": catalog_session_id,
        "old_motif_id": str(record.get("motif_id", "")),
        "record_name": name,
        "review_status_before_classification": str(
            record.get("review_status", "accepted")
        ),
        "classification_status": status,
        "growth_dependent": growth_dependent,
        "broad_growth_record": growth_dependent,
        "accepted_growth_after_classification": False,
        "classification_reason": (
            "Record depends on legacy broad-growth semantics and is superseded "
            "until linked to corrected front-capacity evidence."
            if growth_dependent
            else "Record has no growth-dependent claim and remains retained."
        ),
        "event_counts_by_kind": dict(record.get("event_counts_by_kind", {})),
        "session_ids": _record_session_ids(record, catalog_session_id),
        "supersession_link": supersession_link,
        "replacement_candidate_count": len(replacement_records),
    }


def _classify_catalog_records(
    *,
    family: str,
    catalog_paths: Sequence[Path],
    replacement_candidates: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for catalog_path in catalog_paths:
        catalog = _read_json(catalog_path)
        catalog_session_id = str(catalog.get("session_id") or _session_id_from_path(catalog_path))
        for record in catalog.get("accepted_motifs", ()):
            if isinstance(record, Mapping):
                records.append(
                    classify_reviewed_record(
                        family=family,
                        catalog_path=catalog_path,
                        catalog_session_id=catalog_session_id,
                        record=record,
                        replacement_candidates=replacement_candidates,
                    )
                )
    return records


def _is_growth_dependent_record(record: Mapping[str, Any]) -> bool:
    counts = record.get("event_counts_by_kind", {})
    if isinstance(counts, Mapping) and int(counts.get("growth", 0) or 0) > 0:
        return True
    name = _record_name(record).lower()
    if "growth" in name:
        return True
    fields = (
        record.get("predicted_evidence_fields", ()),
        record.get("observed_evidence_fields", ()),
        record.get("source_construct_kinds", ()),
        record.get("source_term_kinds", ()),
    )
    for values in fields:
        if _sequence_contains_growth(values):
            return True
    evidence_fields = record.get("evidence_fields", {})
    if isinstance(evidence_fields, Mapping):
        for values in evidence_fields.values():
            if _sequence_contains_growth(values):
                return True
    selector_results = record.get("selector_results", ())
    if isinstance(selector_results, Sequence) and not isinstance(selector_results, str):
        for item in selector_results:
            if isinstance(item, Mapping) and _mapping_contains_growth(item):
                return True
    return False


def _mapping_contains_growth(value: Mapping[str, Any]) -> bool:
    for item in value.values():
        if isinstance(item, str) and "growth" in item.lower():
            return True
        if isinstance(item, Mapping) and _mapping_contains_growth(item):
            return True
        if _sequence_contains_growth(item):
            return True
    return False


def _sequence_contains_growth(values: Any) -> bool:
    if isinstance(values, str):
        return "growth" in values.lower()
    if not isinstance(values, Sequence):
        return False
    return any(isinstance(item, str) and "growth" in item.lower() for item in values)


def _load_replacement_candidates(
    corrected_selector_manifest_path: str | Path | None,
) -> Mapping[str, Sequence[Mapping[str, Any]]]:
    if corrected_selector_manifest_path is None:
        return {}
    path = Path(corrected_selector_manifest_path)
    if not path.exists():
        return {}
    manifest = _read_json(path)
    candidates: dict[str, list[Mapping[str, Any]]] = {}
    for item in manifest.get("motifs", ()):
        if not isinstance(item, Mapping):
            continue
        fixture_name = str(item.get("fixture_name", ""))
        key = _replacement_key(fixture_name)
        candidates.setdefault(key, []).append(
            {
                "fixture_name": fixture_name,
                "motif_id": str(item.get("motif_id", "")),
                "source_session_id": str(item.get("source_session_id", "")),
                "confidence_label": str(item.get("confidence_label", "")),
                "evidence_status": str(item.get("evidence_status", "")),
            }
        )
    return {key: tuple(values) for key, values in candidates.items()}


def _replacement_key(name: str) -> str:
    key = name
    if key.startswith("corrected_"):
        key = key.removeprefix("corrected_")
    return key


def _record_name(record: Mapping[str, Any]) -> str:
    for key in ("fixture_name", "seed_name", "lane", "lane_name"):
        value = record.get(key)
        if value:
            return str(value)
    return str(record.get("motif_id", "unknown_record"))


def _record_session_ids(record: Mapping[str, Any], fallback: str) -> list[str]:
    session_ids = record.get("session_ids")
    if isinstance(session_ids, Sequence) and not isinstance(session_ids, str):
        return [str(item) for item in session_ids]
    source_session_id = record.get("source_session_id")
    if source_session_id:
        return [str(source_session_id)]
    return [fallback]


def _classification_payload(
    *,
    session_id: str,
    session_root: Path,
    records: Sequence[Mapping[str, Any]],
    grc9_catalog_paths: Sequence[Path],
    grcl9_catalog_paths: Sequence[Path],
    corrected_selector_manifest_path: Path | None,
) -> dict[str, Any]:
    status_counts = Counter(str(record["classification_status"]) for record in records)
    family_status_counts: dict[str, Counter[str]] = {}
    for record in records:
        family = str(record["family"])
        family_status_counts.setdefault(family, Counter())[str(record["classification_status"])] += 1
    superseded = [
        record for record in records if record["classification_status"] == SUPERSEDED_STATUS
    ]
    retained = [
        record for record in records if record["classification_status"] == RETAINED_STATUS
    ]
    return {
        "classification_version": GROWTH_RECORD_CLASSIFICATION_VERSION,
        "session_id": session_id,
        "session_root": str(session_root),
        "source_reference": "implementation/GRC9-GRCL9-GrowthCorrection-Plan.md",
        "grc9_catalog_paths": [str(path) for path in grc9_catalog_paths],
        "grcl9_catalog_paths": [str(path) for path in grcl9_catalog_paths],
        "corrected_selector_manifest_path": (
            str(corrected_selector_manifest_path)
            if corrected_selector_manifest_path is not None
            else None
        ),
        "classification_policy": {
            "growth_dependent_rule": (
                "growth event counts, growth-bearing names, growth selectors, "
                "or growth source constructs/terms mark the historical record affected"
            ),
            "superseded_status": SUPERSEDED_STATUS,
            "retained_status": RETAINED_STATUS,
            "accepted_growth_after_classification": 0,
        },
        "records": list(records),
        "superseded_records": superseded,
        "retained_non_growth_records": retained,
        "summary": {
            "reviewed_record_count": len(records),
            "retained_non_growth_count": len(retained),
            "superseded_count": len(superseded),
            "accepted_growth_after_classification_count": 0,
            "status_counts": dict(sorted(status_counts.items())),
            "family_status_counts": {
                family: dict(sorted(counts.items()))
                for family, counts in sorted(family_status_counts.items())
            },
            "superseded_with_replacement_candidate_count": sum(
                1 for record in superseded if int(record["replacement_candidate_count"]) > 0
            ),
        },
    }


def _report_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "classification_version": payload["classification_version"],
        "session_id": payload["session_id"],
        "summary": payload["summary"],
        "superseded_old_motif_ids": [
            record["old_motif_id"] for record in payload["superseded_records"]
        ],
        "retained_old_motif_ids": [
            record["old_motif_id"] for record in payload["retained_non_growth_records"]
        ],
    }


def _session_manifest(payload: Mapping[str, Any]) -> dict[str, Any]:
    session_id = str(payload["session_id"])
    return {
        "session_id": session_id,
        "session_kind": "growth_correction_record_classification",
        "classification_version": payload["classification_version"],
        "source_reference": payload["source_reference"],
        "source_catalog_paths": [
            *payload["grc9_catalog_paths"],
            *payload["grcl9_catalog_paths"],
        ],
        "corrected_selector_manifest_path": payload["corrected_selector_manifest_path"],
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.telemetry.grc9_grcl9_growth_record_classification --session-id {session_id}"
        ),
        "summary": payload["summary"],
    }


def _summary_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    family_counts = summary["family_status_counts"]
    lines = [
        "# Growth Record Classification",
        "",
        f"- Session: `{payload['session_id']}`",
        f"- Version: `{payload['classification_version']}`",
        f"- Reviewed records: {summary['reviewed_record_count']}",
        f"- Retained non-growth records: {summary['retained_non_growth_count']}",
        f"- Superseded growth-dependent records: {summary['superseded_count']}",
        "- Accepted growth after classification: 0",
        "",
        "## Family Counts",
        "",
    ]
    for family, counts in family_counts.items():
        retained = counts.get(RETAINED_STATUS, 0)
        superseded = counts.get(SUPERSEDED_STATUS, 0)
        lines.append(f"- `{family}`: retained {retained}, superseded {superseded}")
    lines.extend(
        [
            "",
            "Superseded records keep their old motif ids under `supersession_link`.",
            "They are not counted as accepted growth until a later corrected catalog pass.",
            "",
        ]
    )
    return "\n".join(lines)


def _append_experimental_log(path: Path, payload: Mapping[str, Any]) -> None:
    entry = (
        f"\n## {payload['session_id']} - Growth Record Classification\n\n"
        f"- Reviewed records: {payload['summary']['reviewed_record_count']}\n"
        f"- Retained non-growth records: {payload['summary']['retained_non_growth_count']}\n"
        f"- Superseded records: {payload['summary']['superseded_count']}\n"
        f"- Artifact: `{payload['session_root']}/growth_record_classification.json`\n"
    )
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if f"## {payload['session_id']} - Growth Record Classification" in text:
            return
        path.write_text(text.rstrip() + "\n" + entry, encoding="utf-8")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# GRCL-9 Experimental Log\n" + entry, encoding="utf-8")


def _session_id_from_path(path: Path) -> str:
    parts = path.parts
    for part in reversed(parts):
        if part.startswith("S") and len(part) == 5:
            return part
    return "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing classification input: {path}")
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
        description="Classify reviewed GRC9/GRCL-9 records affected by growth correction."
    )
    parser.add_argument("--session-id", default="S0034")
    parser.add_argument("--output-root", default=str(GRCL9_REPLAY_ROOT))
    parser.add_argument(
        "--corrected-selector-manifest",
        default=str(DEFAULT_CORRECTED_SELECTOR_MANIFEST_PATH),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    session = run_growth_record_classification(
        session_id=args.session_id,
        output_root=args.output_root,
        corrected_selector_manifest_path=args.corrected_selector_manifest,
    )
    print(json.dumps(session.to_mapping(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

