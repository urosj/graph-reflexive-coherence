"""Corrected GRCL-9 growth catalog generation."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .grcl9_replay import GRCL9_REPLAY_ROOT


GRCL9_CORRECTED_GROWTH_CATALOG_VERSION = "grcl9_corrected_growth_catalog_v1"
DEFAULT_SELECTOR_MANIFEST_PATH = (
    Path("outputs/grcl9/lowering/sessions/S0033/selector_manifest.json")
)
DEFAULT_GROWTH_CLASSIFICATION_PATH = (
    Path("outputs/grcl9/lowering/sessions/S0034/growth_record_classification.json")
)
_REQUIRED_SELECTOR_IDS = frozenset(
    {
        "front_capacity_mode",
        "no_legacy_broad_growth",
        "front_growth_provenance_consistent",
    }
)


@dataclass(frozen=True)
class GRCL9CorrectedGrowthCatalogSession:
    """Result from a corrected GRCL-9 growth catalog run."""

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


def run_grcl9_corrected_growth_catalog(
    *,
    session_id: str = "S0036",
    output_root: str | Path = GRCL9_REPLAY_ROOT,
    selector_manifest_path: str | Path = DEFAULT_SELECTOR_MANIFEST_PATH,
    growth_classification_path: str | Path = DEFAULT_GROWTH_CLASSIFICATION_PATH,
) -> GRCL9CorrectedGrowthCatalogSession:
    """Publish a corrected GRCL-9 source/lowering growth catalog."""

    if not session_id.startswith("S"):
        raise ValueError("session_id must be an S-prefixed session id")
    root = Path(output_root)
    session_root = root / "sessions" / session_id
    reports_root = session_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    selector_manifest = _read_json(Path(selector_manifest_path))
    superseded = _load_superseded_grcl9_records(Path(growth_classification_path))
    visual_records = _load_visual_records(root, selector_manifest)
    accepted_growth: list[dict[str, Any]] = []
    accepted_controls: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for motif in selector_manifest.get("motifs", ()):
        if not isinstance(motif, Mapping):
            continue
        record = review_corrected_grcl9_growth_record(
            motif=motif,
            superseded=superseded,
            visual=visual_records.get(str(motif.get("fixture_name", "")), {}),
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
        selector_manifest_path=Path(selector_manifest_path),
        growth_classification_path=Path(growth_classification_path),
        source_session_ids=tuple(str(item) for item in selector_manifest.get("source_session_ids", ())),
        accepted_growth=accepted_growth,
        accepted_controls=accepted_controls,
        rejected=rejected,
    )
    report = _report_payload(catalog)

    catalog_path = session_root / "corrected_grcl9_growth_catalog.json"
    report_path = reports_root / "corrected_grcl9_growth_catalog_report.json"
    summary_path = reports_root / "corrected_grcl9_growth_catalog_summary.md"
    _write_json(catalog_path, catalog)
    _write_json(report_path, report)
    _write_text(summary_path, _summary_markdown(catalog))
    _write_json(session_root / "session_manifest.json", _session_manifest(catalog))
    _write_readme(session_root, catalog)
    _append_experimental_log(root / "ExperimentalLog.md", catalog)

    summary = catalog["summary"]
    return GRCL9CorrectedGrowthCatalogSession(
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


def review_corrected_grcl9_growth_record(
    *,
    motif: Mapping[str, Any],
    superseded: Sequence[Mapping[str, Any]] = (),
    visual: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Review one corrected GRCL-9 selector-backed record."""

    fixture_name = str(motif["fixture_name"])
    telemetry_root = Path(str(motif["telemetry_root"]))
    run_summary = _read_json(telemetry_root / "run_summary.json")
    events = _read_jsonl(telemetry_root / "events.jsonl")
    source = _read_json(Path(str(motif["source_fixture_path"])))
    lowered_state_path = Path(str(motif["lowered_state_path"]))
    visual = visual or {}

    grc9_ext = run_summary.get("family_extensions", {}).get("grc9", {})
    grcl9_ext = run_summary.get("family_extensions", {}).get("grcl9", {})
    backend = grc9_ext.get("backend_summary", {})
    growth_summary = grc9_ext.get("growth_summary", {})
    growth_count = int(growth_summary.get("growth_count", 0) or 0)
    front_growth_count = int(growth_summary.get("front_capacity_growth_count", 0) or 0)
    legacy_growth_count = int(growth_summary.get("legacy_broad_growth_count", 0) or 0)
    mode = str(
        grcl9_ext.get(
            "growth_parent_eligibility_mode",
            backend.get("growth_parent_eligibility_mode", ""),
        )
    )
    source_constructs = tuple(
        item for item in source.get("constructs", ()) if isinstance(item, Mapping)
    )
    growth_constructs = tuple(
        item for item in source_constructs if item.get("construct_kind") == "growth_locus"
    )
    growth_events = tuple(event for event in events if event.get("event_kind") == "growth")
    event_evidence = tuple(_growth_event_evidence(event) for event in growth_events)
    passed_selectors = set(str(item) for item in motif.get("passed_selector_ids", ()))

    selectors_ok = _REQUIRED_SELECTOR_IDS.issubset(passed_selectors)
    motif_accepted = motif.get("evidence_status") == "accepted"
    mode_ok = mode == "grc9_front_capacity"
    no_legacy = legacy_growth_count == 0 and grcl9_ext.get("legacy_broad_growth_non_evidence") is False
    front_count_ok = front_growth_count == growth_count
    event_count_ok = len(growth_events) == growth_count
    event_evidence_ok = all(
        evidence.get("grc9_parent_eligibility_mode") == "grc9_front_capacity"
        and evidence.get("grc9_front_growth_provenance_present") is True
        and evidence.get("grc9_legacy_broad_growth") is False
        and evidence.get("grcl9_growth_parent_eligibility_mode") == "grc9_front_capacity"
        and evidence.get("grcl9_legacy_broad_growth_non_evidence") is False
        for evidence in event_evidence
    )
    source_growth_ok = all(
        construct.get("growth_semantics") == "front_capacity"
        and bool(construct.get("front_capacity_source"))
        for construct in growth_constructs
    )

    accepted_growth = (
        motif_accepted
        and selectors_ok
        and mode_ok
        and no_legacy
        and growth_count > 0
        and front_count_ok
        and event_count_ok
        and event_evidence_ok
        and source_growth_ok
    )
    accepted_control = (
        motif_accepted
        and selectors_ok
        and mode_ok
        and no_legacy
        and growth_count == 0
        and front_growth_count == 0
    )
    review_status = (
        "accepted_corrected_growth"
        if accepted_growth
        else "accepted_corrected_control"
        if accepted_control
        else "rejected"
    )
    failure_reasons: list[str] = []
    if not motif_accepted:
        failure_reasons.append("selector manifest evidence_status is not accepted")
    if not selectors_ok:
        failure_reasons.append("required front-capacity selector ids did not pass")
    if not mode_ok:
        failure_reasons.append("GRCL-9 growth parent eligibility mode is not grc9_front_capacity")
    if not no_legacy:
        failure_reasons.append("legacy broad-growth marker is present")
    if growth_count > 0 and not front_count_ok:
        failure_reasons.append("front-capacity growth count does not match growth count")
    if growth_count > 0 and not event_count_ok:
        failure_reasons.append("growth event rows do not match run-summary growth count")
    if growth_count > 0 and not event_evidence_ok:
        failure_reasons.append("growth event rows lack GRC9/GRCL-9 front-capacity evidence")
    if growth_count > 0 and not source_growth_ok:
        failure_reasons.append("source growth constructs are not front-capacity constructs")

    return {
        "motif_id": str(motif.get("motif_id", f"grcl9-corrected-{_slug(fixture_name)}")),
        "review_status": review_status,
        "family": "grcl9",
        "source_session_id": str(motif.get("source_session_id", "")),
        "fixture_name": fixture_name,
        "manifest_entry_id": str(motif.get("manifest_entry_id", "")),
        "run_id": str(motif.get("run_id", "")),
        "requested_steps": int(motif.get("requested_steps", 0) or 0),
        "confidence_label": str(motif.get("confidence_label", "")),
        "selector_evidence_status": str(motif.get("evidence_status", "")),
        "event_counts_by_kind": dict(motif.get("event_counts_by_kind", {})),
        "passed_selector_ids": list(motif.get("passed_selector_ids", ())),
        "expected_selector_ids": list(motif.get("expected_selector_ids", ())),
        "front_capacity_evidence": {
            "grcl9_growth_parent_eligibility_mode": mode,
            "grcl9_growth_semantics_status": str(
                grcl9_ext.get("growth_semantics_status", "")
            ),
            "growth_count": growth_count,
            "front_capacity_growth_count": front_growth_count,
            "legacy_broad_growth_count": legacy_growth_count,
            "source_growth_construct_count": len(growth_constructs),
            "source_front_capacity_growth_construct_count": sum(
                1
                for construct in growth_constructs
                if construct.get("growth_semantics") == "front_capacity"
            ),
            "growth_event_row_count": len(growth_events),
            "growth_event_evidence": list(event_evidence),
            "visual_evidence_status": str(visual.get("evidence_status", "")),
            "visual_growth_parent_eligibility_mode": str(
                visual.get("growth_parent_eligibility_mode", "")
            ),
        },
        "supersedes_old_motif_ids": _superseded_ids_for_fixture(
            fixture_name=fixture_name,
            superseded=superseded,
        ),
        "artifact_links": {
            "source_fixture": str(motif.get("source_fixture_path", "")),
            "lowered_state": str(lowered_state_path),
            "telemetry_root": str(telemetry_root),
            "run_summary": str(telemetry_root / "run_summary.json"),
            "events": str(telemetry_root / "events.jsonl"),
            "steps": str(telemetry_root / "steps.jsonl"),
            "graph_checkpoint_index": str(telemetry_root / "graph_checkpoints" / "index.json"),
            "visualization": str(visual.get("visualization_dir", "")),
            "visual_overlay_summary": str(visual.get("grcl9_overlay_summary_path", "")),
        },
        "failure_reasons": failure_reasons,
        "non_claims": [
            "GRC9 runtime remains the execution surface",
            "GRCL-9 source declares front-growth preconditions but not solved events",
            "legacy broad-growth source records are replay-only diagnostics",
            "no GRCV3 hierarchy, Lorentzian causal layer, or observer-local semantics are claimed",
        ],
    }


def _growth_event_evidence(event: Mapping[str, Any]) -> Mapping[str, Any]:
    grc9_ext = event.get("family_extensions", {}).get("grc9", {})
    grcl9_ext = event.get("family_extensions", {}).get("grcl9", {})
    growth = grc9_ext.get("growth_evidence", {})
    return {
        "grc9_parent_eligibility_mode": growth.get("parent_eligibility_mode"),
        "grc9_parent_capacity_source": growth.get("parent_capacity_source"),
        "grc9_front_growth_provenance_present": growth.get(
            "front_growth_provenance_present"
        ),
        "grc9_legacy_broad_growth": growth.get("legacy_broad_growth"),
        "grc9_selected_parent_port": growth.get("selected_parent_port"),
        "grcl9_growth_parent_eligibility_mode": grcl9_ext.get(
            "growth_parent_eligibility_mode"
        ),
        "grcl9_growth_semantics_status": grcl9_ext.get("growth_semantics_status"),
        "grcl9_legacy_broad_growth_non_evidence": grcl9_ext.get(
            "legacy_broad_growth_non_evidence"
        ),
    }


def _load_superseded_grcl9_records(
    classification_path: Path,
) -> Sequence[Mapping[str, Any]]:
    if not classification_path.exists():
        return ()
    classification = _read_json(classification_path)
    return tuple(
        record
        for record in classification.get("superseded_records", ())
        if isinstance(record, Mapping) and record.get("family") == "grcl9"
    )


def _load_visual_records(
    output_root: Path,
    selector_manifest: Mapping[str, Any],
) -> Mapping[str, Mapping[str, Any]]:
    records: dict[str, Mapping[str, Any]] = {}
    for source_session_id in selector_manifest.get("source_session_ids", ()):
        visual_path = (
            output_root
            / "sessions"
            / str(source_session_id)
            / "visualizations"
            / "visualization_manifest.json"
        )
        if not visual_path.exists():
            continue
        visual_manifest = _read_json(visual_path)
        for lane in visual_manifest.get("lanes", ()):
            if isinstance(lane, Mapping) and lane.get("fixture_name"):
                records[str(lane["fixture_name"])] = lane
    return records


def _superseded_ids_for_fixture(
    *,
    fixture_name: str,
    superseded: Sequence[Mapping[str, Any]],
) -> list[str]:
    key = fixture_name.removeprefix("corrected_")
    ids: list[str] = []
    seen: set[str] = set()
    for record in superseded:
        if record.get("record_name") != key or not record.get("old_motif_id"):
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
    selector_manifest_path: Path,
    growth_classification_path: Path,
    source_session_ids: Sequence[str],
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
        "catalog_version": GRCL9_CORRECTED_GROWTH_CATALOG_VERSION,
        "session_id": session_id,
        "session_root": str(session_root),
        "source_reference": "implementation/GRC9-GRCL9-GrowthCorrection-Plan.md",
        "selector_manifest_path": str(selector_manifest_path),
        "growth_classification_path": str(growth_classification_path),
        "source_session_ids": list(source_session_ids),
        "review_policy": {
            "accepted_growth": (
                "selector-backed accepted record with grc9_front_capacity mode, "
                "no legacy broad growth, matching front-capacity growth counts, "
                "GRC9/GRCL-9 event-row provenance, and front-capacity source constructs"
            ),
            "accepted_control": (
                "selector-backed accepted record under grc9_front_capacity with "
                "zero growth and zero legacy broad-growth count"
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
                for record in [*accepted_growth, *accepted_controls]
            ),
        },
        "non_claims": [
            "GRCL-9 source/lowering evidence does not inject runtime events",
            "legacy broad-growth source records remain replay-only diagnostics",
            "native GRC9 runtime evidence is published separately",
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
        "rejected_motif_ids": [record["motif_id"] for record in catalog["rejected_motifs"]],
    }


def _session_manifest(catalog: Mapping[str, Any]) -> dict[str, Any]:
    session_id = str(catalog["session_id"])
    return {
        "session_id": session_id,
        "session_kind": "grcl9_corrected_growth_catalog",
        "catalog_version": catalog["catalog_version"],
        "source_session_ids": catalog["source_session_ids"],
        "selector_manifest_path": catalog["selector_manifest_path"],
        "growth_classification_path": catalog["growth_classification_path"],
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.telemetry.grcl9_corrected_growth_catalog --session-id {session_id}"
        ),
        "summary": catalog["summary"],
    }


def _summary_markdown(catalog: Mapping[str, Any]) -> str:
    summary = catalog["summary"]
    lines = [
        "# Corrected GRCL-9 Growth Catalog",
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
            f"- `{record['fixture_name']}` from `{record['source_session_id']}` "
            f"supersedes: {links}"
        )
    lines.extend(["", "## Accepted Controls", ""])
    for record in catalog["accepted_corrected_control_motifs"]:
        links = ", ".join(record.get("supersedes_old_motif_ids", ())) or "none"
        lines.append(
            f"- `{record['fixture_name']}` from `{record['source_session_id']}` "
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
        f"\n## {catalog['session_id']} - Corrected GRCL-9 Growth Catalog\n\n"
        f"- Selector manifest: `{catalog['selector_manifest_path']}`\n"
        f"- Accepted corrected growth motifs: "
        f"{catalog['summary']['accepted_corrected_growth_count']}\n"
        f"- Accepted corrected controls: "
        f"{catalog['summary']['accepted_corrected_control_count']}\n"
        f"- Supersession links: {catalog['summary']['supersession_link_count']}\n"
        f"- Artifact: `{catalog['session_root']}/corrected_grcl9_growth_catalog.json`\n"
    )
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if f"## {catalog['session_id']} - Corrected GRCL-9 Growth Catalog" in text:
            return
        path.write_text(text.rstrip() + "\n" + entry, encoding="utf-8")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# GRCL-9 Experimental Log\n" + entry, encoding="utf-8")


def _slug(value: str) -> str:
    return value.replace("_", "-")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing GRCL-9 corrected catalog input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> tuple[dict[str, Any], ...]:
    if not path.exists():
        raise FileNotFoundError(f"missing GRCL-9 corrected catalog input: {path}")
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
    parser = argparse.ArgumentParser(description="Publish corrected GRCL-9 growth catalog.")
    parser.add_argument("--session-id", default="S0036")
    parser.add_argument("--output-root", default=str(GRCL9_REPLAY_ROOT))
    parser.add_argument("--selector-manifest", default=str(DEFAULT_SELECTOR_MANIFEST_PATH))
    parser.add_argument(
        "--growth-classification-path",
        default=str(DEFAULT_GROWTH_CLASSIFICATION_PATH),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    session = run_grcl9_corrected_growth_catalog(
        session_id=args.session_id,
        output_root=args.output_root,
        selector_manifest_path=args.selector_manifest,
        growth_classification_path=args.growth_classification_path,
    )
    print(json.dumps(session.to_mapping(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

