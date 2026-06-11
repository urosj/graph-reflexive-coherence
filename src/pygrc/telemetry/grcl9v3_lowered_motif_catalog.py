"""Reviewed GRCL-9V3 lowered-source motif catalog generation."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
import hashlib
import json
from pathlib import Path
from typing import Any

from .grcl9v3_replay import GRCL9V3_REPLAY_ROOT


GRCL9V3_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION = (
    "grcl9v3_reviewed_lowered_motif_catalog_v1"
)
DEFAULT_GRCL9V3_CATALOG_SELECTOR_SESSIONS = (
    "S0011",
    "S0017",
    "S0020",
    "S0023",
    "S0026",
    "S0031",
    "S0036",
    "S0039",
    "S0041",
    "S0044",
    "S0047",
    "S0050",
    "S0053",
    "S0056",
    "S0067",
)
DEFAULT_GRCL9V3_CATALOG_VISUAL_SESSIONS = {
    "S0011": "S0012",
    "S0017": "S0018",
    "S0020": "S0021",
    "S0023": "S0024",
    "S0026": "S0027",
    "S0031": "S0032",
    "S0044": "S0045",
    "S0047": "S0048",
    "S0050": "S0051",
    "S0053": "S0054",
    "S0056": "S0057",
    "S0067": "S0070",
}
_GROWTH_SELECTOR_IDS = frozenset(
    {
        "growth_events",
        "no_growth_events",
        "growth_reduction",
        "front_growth_provenance",
        "closed_front_no_growth",
        "growth_before_collapse",
        "growth_collapse_relay_diagnostics",
    }
)
_CORRECTED_GROWTH_SELECTOR_IDS = frozenset(
    {
        "front_growth_provenance",
        "closed_front_no_growth",
    }
)


@dataclass(frozen=True)
class GRCL9V3ReviewedLoweredMotifCatalogSession:
    """Result from a reviewed GRCL-9V3 lowered motif catalog run."""

    session_id: str
    session_root: Path
    catalog_path: Path
    review_report_path: Path
    summary_path: Path
    accepted_count: int
    strong_candidate_count: int
    diagnostic_count: int
    superseded_count: int
    rejected_count: int

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "session_root": str(self.session_root),
            "catalog_path": str(self.catalog_path),
            "review_report_path": str(self.review_report_path),
            "summary_path": str(self.summary_path),
            "accepted_count": self.accepted_count,
            "strong_candidate_count": self.strong_candidate_count,
            "diagnostic_count": self.diagnostic_count,
            "superseded_count": self.superseded_count,
            "rejected_count": self.rejected_count,
        }


def run_grcl9v3_reviewed_lowered_motif_catalog(
    *,
    session_id: str = "S0072",
    selector_session_ids: Sequence[str] = DEFAULT_GRCL9V3_CATALOG_SELECTOR_SESSIONS,
    visual_session_ids_by_selector: Mapping[str, str] | None = None,
    output_root: str | Path = GRCL9V3_REPLAY_ROOT,
) -> GRCL9V3ReviewedLoweredMotifCatalogSession:
    """Promote reviewed GRCL-9V3 lowered-source evidence into a catalog."""

    _validate_session_id(session_id)
    if not selector_session_ids:
        raise ValueError("selector_session_ids must not be empty")
    for selector_session_id in selector_session_ids:
        _validate_session_id(selector_session_id)
    visual_map = dict(DEFAULT_GRCL9V3_CATALOG_VISUAL_SESSIONS)
    if visual_session_ids_by_selector is not None:
        visual_map.update(
            {
                str(selector): str(visual)
                for selector, visual in visual_session_ids_by_selector.items()
            }
        )
    for visual_session_id in visual_map.values():
        _validate_session_id(visual_session_id)

    root = Path(output_root)
    session_root = root / "sessions" / session_id
    reports_root = session_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    review_records: list[dict[str, Any]] = []
    for selector_session_id in selector_session_ids:
        selector_session_root = root / "sessions" / selector_session_id
        visual_session_id = visual_map.get(selector_session_id)
        visual_records = (
            _visual_records_by_fixture(root / "sessions" / visual_session_id)
            if visual_session_id
            else {}
        )
        review_records.extend(
            _review_selector_session(
                selector_session_id=selector_session_id,
                selector_session_root=selector_session_root,
                visual_session_id=visual_session_id,
                visual_records=visual_records,
            )
        )
    _apply_duplicate_links(review_records)

    catalog = _catalog_payload(
        session_id=session_id,
        session_root=session_root,
        output_root=root,
        selector_session_ids=tuple(selector_session_ids),
        review_records=tuple(review_records),
    )
    report = _review_report_payload(
        session_id=session_id,
        selector_session_ids=tuple(selector_session_ids),
        review_records=tuple(review_records),
    )

    catalog_path = session_root / "reviewed_grcl9v3_lowered_motif_catalog.json"
    review_report_path = (
        reports_root / "reviewed_grcl9v3_lowered_motif_catalog_report.json"
    )
    summary_path = reports_root / "reviewed_grcl9v3_lowered_motif_catalog_summary.md"
    _write_json(catalog_path, catalog)
    _write_json(review_report_path, report)
    _write_text(summary_path, _summary_markdown(catalog))
    _write_json(
        session_root / "session_manifest.json",
        _session_manifest(
            session_id=session_id,
            catalog_path=catalog_path,
            review_report_path=review_report_path,
            summary_path=summary_path,
            selector_session_ids=tuple(selector_session_ids),
            output_root=root,
        ),
    )
    _write_readme(session_root, catalog)
    _write_experimental_log(root / "ExperimentalLog.md", catalog)

    status_counts = Counter(str(item["review_status"]) for item in review_records)
    return GRCL9V3ReviewedLoweredMotifCatalogSession(
        session_id=session_id,
        session_root=session_root,
        catalog_path=catalog_path,
        review_report_path=review_report_path,
        summary_path=summary_path,
        accepted_count=status_counts.get("accepted", 0),
        strong_candidate_count=status_counts.get("strong_candidate", 0),
        diagnostic_count=status_counts.get("diagnostic", 0),
        superseded_count=status_counts.get(
            "superseded_by_growth_semantics_correction", 0
        ),
        rejected_count=status_counts.get("rejected", 0),
    )


def _validate_session_id(session_id: str) -> None:
    if not session_id.startswith("S") or not session_id[1:].isdigit():
        raise ValueError("session ids must use S0001-style formatting")


def _review_selector_session(
    *,
    selector_session_id: str,
    selector_session_root: Path,
    visual_session_id: str | None,
    visual_records: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    selector_manifest_path = selector_session_root / "selector_manifest.json"
    selector_report_path = (
        selector_session_root / "reports" / "selector_validation_report.json"
    )
    if not selector_manifest_path.exists():
        raise FileNotFoundError(f"missing selector manifest: {selector_manifest_path}")
    if not selector_report_path.exists():
        raise FileNotFoundError(f"missing selector report: {selector_report_path}")
    selector_manifest = _read_json(selector_manifest_path)
    selector_report = _read_json(selector_report_path)
    motifs_by_lane = {
        str(item.get("lane", item.get("fixture_name", ""))): item
        for item in selector_manifest.get("motifs", ())
        if isinstance(item, Mapping)
    }
    records: list[dict[str, Any]] = []
    for validation in selector_report.get("validations", ()):
        if not isinstance(validation, Mapping):
            continue
        lane_name = str(validation.get("lane_name", validation.get("fixture_name", "")))
        records.append(
            _review_validation(
                selector_session_id=selector_session_id,
                selector_manifest_path=selector_manifest_path,
                selector_report_path=selector_report_path,
                validation=validation,
                motif=motifs_by_lane.get(lane_name, {}),
                visual_session_id=visual_session_id,
                visual=visual_records.get(str(validation.get("fixture_name", lane_name)), {}),
            )
        )
    return tuple(records)


def _visual_records_by_fixture(visual_session_root: Path) -> Mapping[str, Mapping[str, Any]]:
    report_path = visual_session_root / "reports" / "visual_review_report.json"
    if not report_path.exists():
        return {}
    report = _read_json(report_path)
    return {
        str(record.get("fixture_name", "")): record
        for record in report.get("records", ())
        if isinstance(record, Mapping)
    }


def _review_validation(
    *,
    selector_session_id: str,
    selector_manifest_path: Path,
    selector_report_path: Path,
    validation: Mapping[str, Any],
    motif: Mapping[str, Any],
    visual_session_id: str | None,
    visual: Mapping[str, Any],
) -> dict[str, Any]:
    fixture_name = str(validation["fixture_name"])
    source_session_id = str(validation["source_session_id"])
    source_fixture_path = Path(str(validation["source_fixture_path"]))
    lowered_state_path = Path(str(validation["lowered_state_path"]))
    telemetry_root = Path(str(validation["telemetry_root"]))
    artifact_root = telemetry_root.parent
    run_summary_path = telemetry_root / "run_summary.json"
    events_path = telemetry_root / "events.jsonl"
    steps_path = telemetry_root / "steps.jsonl"
    checkpoint_index_path = telemetry_root / "graph_checkpoints" / "index.json"
    required_paths = {
        "compiled_source": source_fixture_path,
        "lowered_state": lowered_state_path,
        "selector_manifest": selector_manifest_path,
        "selector_report": selector_report_path,
        "telemetry_run_summary": run_summary_path,
        "telemetry_events": events_path,
        "telemetry_steps": steps_path,
        "graph_checkpoint_index": checkpoint_index_path,
    }
    missing = [name for name, path in required_paths.items() if not path.exists()]
    source = _read_json(source_fixture_path) if source_fixture_path.exists() else {}
    lowered = _read_json(lowered_state_path) if lowered_state_path.exists() else {}
    run_summary = _read_json(run_summary_path) if run_summary_path.exists() else {}
    source_selectors = tuple(
        str(item) for item in validation.get("source_expected_selector_ids", ())
    )
    expanded_selectors = tuple(
        str(item) for item in validation.get("expanded_selector_ids", ())
    )
    confidence_label = str(validation.get("confidence_label", "rejected"))
    missing_surfaces = tuple(
        str(item) for item in validation.get("missing_surface_selector_ids", ())
    )
    growth_review = _growth_review_policy(
        source_selectors=source_selectors,
        expanded_selectors=expanded_selectors,
        run_summary=run_summary,
    )
    review_status, review_notes = _review_status(
        confidence_label=confidence_label,
        missing=tuple(missing),
        missing_surfaces=missing_surfaces,
        growth_review=growth_review,
    )
    visual_available = bool(visual)
    visual_links = _visual_links(visual)
    source_provenance = source.get("compiled_source_provenance", {})
    seed_reference = (
        source_provenance.get("source_seed_reference")
        if isinstance(source_provenance, Mapping)
        else None
    )
    source_construct_kinds = [
        str(item.get("construct_kind", ""))
        for item in source.get("constructs", ())
        if isinstance(item, Mapping) and item.get("construct_kind")
    ]
    motif_registry = lowered.get("cached_quantities", {}).get(
        "grcl9v3_motif_registry", {}
    )
    motif_roles = sorted(
        {
            str(role)
            for item in motif_registry.values()
            if isinstance(item, Mapping)
            for role in item.get("motif_roles", ())
        }
    )
    selector_results = list(validation.get("selector_results", ()))
    entry = {
        "motif_id": _motif_id(selector_session_id, fixture_name),
        "review_status": review_status,
        "review_history": [
            {
                "reviewer": "codex",
                "review_iteration": "GRCL-9V3 Iteration 10",
                "decision": review_status,
                "selector_session_id": selector_session_id,
                "source_session_id": source_session_id,
            }
        ],
        "source_session_id": source_session_id,
        "selector_session_id": selector_session_id,
        "visual_session_id": visual_session_id,
        "fixture_name": fixture_name,
        "phenomenon": str(motif.get("phenomenon", _phenomenon_from_lane(fixture_name))),
        "evidence_class": _evidence_class(fixture_name, source_selectors, growth_review),
        "manifest_entry_id": str(validation.get("manifest_entry_id", "")),
        "control_role": str(validation.get("control_role", "")),
        "run_id": str(validation.get("run_id", "")),
        "requested_steps": int(validation.get("requested_steps", 0)),
        "event_counts_by_kind": dict(validation.get("event_counts_by_kind", {})),
        "confidence_label": confidence_label,
        "confidence_score": int(validation.get("confidence_score", 0)),
        "source_expected_selector_ids": list(source_selectors),
        "expanded_selector_ids": list(expanded_selectors),
        "passed_selector_ids": list(validation.get("passed_selector_ids", ())),
        "missing_selector_ids": list(validation.get("missing_selector_ids", ())),
        "missing_surface_selector_ids": list(missing_surfaces),
        "selector_results": selector_results,
        "growth_review": growth_review,
        "review_notes": review_notes,
        "failure_notes": [
            *([f"missing required artifacts: {', '.join(missing)}"] if missing else []),
            *([f"missing selector surfaces: {', '.join(missing_surfaces)}"] if missing_surfaces else []),
        ],
        "artifact_links": _artifact_links(
            required_paths=required_paths,
            artifact_root=artifact_root,
            source_seed_reference=seed_reference,
            visual_links=visual_links,
        ),
        "source_construct_kinds": source_construct_kinds,
        "source_term_kinds": _source_term_kinds(source),
        "motif_registry": motif_registry,
        "motif_roles": motif_roles,
        "expected_region_cache_names": _expected_region_cache_names(run_summary),
        "visual_available": visual_available,
        "visual_status": str(visual.get("visual_status", "")),
        "connected": bool(visual.get("connected", False)) if visual else None,
        "bridge_edge_count": int(visual.get("bridge_edge_count", 0)) if visual else 0,
        "non_claims": _non_claims(source, growth_review),
        "duplicate_group_id": _duplicate_group_id(
            manifest_entry_id=str(validation.get("manifest_entry_id", "")),
            source_construct_kinds=tuple(source_construct_kinds),
            source_selectors=source_selectors,
            growth_status=str(growth_review["status"]),
        ),
        "duplicate_of": None,
    }
    return entry


def _growth_review_policy(
    *,
    source_selectors: Sequence[str],
    expanded_selectors: Sequence[str],
    run_summary: Mapping[str, Any],
) -> Mapping[str, Any]:
    source_selector_set = set(source_selectors)
    expanded_selector_set = set(expanded_selectors)
    has_growth_claim = bool(source_selector_set & _GROWTH_SELECTOR_IDS) or bool(
        expanded_selector_set & _GROWTH_SELECTOR_IDS
    )
    status = str(
        _get_path(
            run_summary,
            "family_extensions.grcl9v3.growth_semantics_status",
            "none",
        )
    )
    legacy_ids = _get_path(
        run_summary,
        "family_extensions.grcl9v3.legacy_growth_locus_ids",
        (),
    ) or ()
    if isinstance(legacy_ids, Sequence) and not isinstance(legacy_ids, str):
        legacy_ids = [str(item) for item in legacy_ids]
    else:
        legacy_ids = []
    front_selector = bool(
        (source_selector_set | expanded_selector_set) & _CORRECTED_GROWTH_SELECTOR_IDS
    )
    front_capacity = status == "front_capacity" and not legacy_ids
    if not has_growth_claim:
        review = "not_growth_claim"
    elif front_selector and front_capacity:
        review = "corrected_front_growth"
    else:
        review = "superseded_standalone_growth"
    return {
        "has_growth_claim": has_growth_claim,
        "status": review,
        "growth_semantics_status": status,
        "front_growth_selector_present": front_selector,
        "legacy_growth_locus_ids": legacy_ids,
        "paper_facing_eligible": (not has_growth_claim) or review == "corrected_front_growth",
    }


def _review_status(
    *,
    confidence_label: str,
    missing: Sequence[str],
    missing_surfaces: Sequence[str],
    growth_review: Mapping[str, Any],
) -> tuple[str, list[str]]:
    notes: list[str] = []
    if growth_review["status"] == "superseded_standalone_growth":
        notes.append(
            "legacy standalone-growth evidence superseded by Iteration 9 front-growth semantics"
        )
        return "superseded_by_growth_semantics_correction", notes
    if missing or missing_surfaces:
        notes.append("required artifact or selector surface is missing")
        return "rejected", notes
    if confidence_label == "strong_candidate":
        return "accepted", notes
    if confidence_label == "candidate":
        notes.append("candidate retained but not promoted to accepted")
        return "strong_candidate", notes
    if confidence_label == "ambiguous":
        notes.append("ambiguous selector evidence retained for diagnostics")
        return "diagnostic", notes
    notes.append(f"selector confidence label is {confidence_label!r}")
    return "rejected", notes


def _evidence_class(
    fixture_name: str,
    source_selectors: Sequence[str],
    growth_review: Mapping[str, Any],
) -> str:
    if growth_review["status"] == "superseded_standalone_growth":
        return "legacy_growth_diagnostic"
    if fixture_name.startswith("corrected_") or "corrected" in fixture_name:
        return "corrected_front_growth_seed"
    if fixture_name.startswith("cell_") or "_cell_" in fixture_name:
        return "composing_cells_seed"
    if "relay" in fixture_name:
        return "relay_diagnostic"
    if source_selectors:
        return "mechanism_probe"
    return "lowered_source_record"


def _artifact_links(
    *,
    required_paths: Mapping[str, Path],
    artifact_root: Path,
    source_seed_reference: Any,
    visual_links: Mapping[str, str],
) -> Mapping[str, Any]:
    return {
        "source_seed_reference": str(source_seed_reference or ""),
        "compiled_source": str(required_paths["compiled_source"]),
        "lowered_state": str(required_paths["lowered_state"]),
        "selector_manifest": str(required_paths["selector_manifest"]),
        "selector_report": str(required_paths["selector_report"]),
        "telemetry": {
            "root": str(artifact_root / "telemetry"),
            "run_summary": str(required_paths["telemetry_run_summary"]),
            "events": str(required_paths["telemetry_events"]),
            "steps": str(required_paths["telemetry_steps"]),
        },
        "graph_checkpoints": {
            "index": str(required_paths["graph_checkpoint_index"]),
        },
        "visualization": dict(visual_links),
    }


def _visual_links(visual: Mapping[str, Any]) -> Mapping[str, str]:
    if not visual:
        return {}
    return {
        "panel": str(visual.get("boundary_panel_path", "")),
        "overlay": str(visual.get("grcl9v3_overlay_path", "")),
        "overlay_summary": str(visual.get("grcl9v3_overlay_summary_path", "")),
        "graph_sequence": str(visual.get("graph_sequence_path", "")),
        "event_timeline": str(visual.get("event_timeline_path", "")),
        "trajectory": str(visual.get("trajectory_path", "")),
    }


def _non_claims(
    source: Mapping[str, Any],
    growth_review: Mapping[str, Any],
) -> list[str]:
    claims = {
        str(item) for item in source.get("non_claims", ()) if isinstance(item, str)
    }
    claims.update(
        {
            "catalog acceptance is selector-backed telemetry evidence, not source truth",
            "visuals are supporting evidence only",
            "no GRCL-9V3 source-level runtime event injection is claimed",
        }
    )
    if growth_review["status"] == "superseded_standalone_growth":
        claims.add("legacy standalone growth is diagnostic and not paper-facing")
    if growth_review["status"] == "corrected_front_growth":
        claims.add("front growth remains runtime-observed, not source-solved")
    return sorted(claims)


def _expected_region_cache_names(run_summary: Mapping[str, Any]) -> list[str]:
    names = _get_path(
        run_summary,
        "family_extensions.grcl9v3.expected_region_cache_names",
        (),
    ) or ()
    if isinstance(names, Sequence) and not isinstance(names, str):
        return [str(item) for item in names]
    return []


def _source_term_kinds(source: Mapping[str, Any]) -> list[str]:
    provenance = source.get("compiled_source_provenance", {})
    if not isinstance(provenance, Mapping):
        return []
    terms = provenance.get("source_terms", ())
    return sorted(
        {
            str(item.get("term_kind"))
            for item in terms
            if isinstance(item, Mapping) and item.get("term_kind")
        }
    )


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


def _duplicate_group_id(
    *,
    manifest_entry_id: str,
    source_construct_kinds: Sequence[str],
    source_selectors: Sequence[str],
    growth_status: str,
) -> str:
    digest = hashlib.sha256(
        json.dumps(
            {
                "constructs": list(source_construct_kinds),
                "selectors": list(source_selectors),
                "growth_status": growth_status,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()[:12]
    return f"dup_{manifest_entry_id}_{digest}"


def _apply_duplicate_links(records: list[dict[str, Any]]) -> None:
    first_by_group: dict[str, str] = {}
    for record in records:
        if record["review_status"] not in {"accepted", "strong_candidate"}:
            continue
        group_id = str(record["duplicate_group_id"])
        first = first_by_group.setdefault(group_id, str(record["motif_id"]))
        if first != record["motif_id"]:
            record["duplicate_of"] = first


def _catalog_payload(
    *,
    session_id: str,
    session_root: Path,
    output_root: Path,
    selector_session_ids: tuple[str, ...],
    review_records: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    status_counts = Counter(str(item["review_status"]) for item in review_records)
    evidence_counts = Counter(str(item["evidence_class"]) for item in review_records)
    accepted = [
        item for item in review_records if item["review_status"] == "accepted"
    ]
    strong = [
        item for item in review_records if item["review_status"] == "strong_candidate"
    ]
    diagnostics = [
        item for item in review_records if item["review_status"] == "diagnostic"
    ]
    superseded = [
        item
        for item in review_records
        if item["review_status"] == "superseded_by_growth_semantics_correction"
    ]
    rejected = [
        item for item in review_records if item["review_status"] == "rejected"
    ]
    duplicate_link_count = sum(
        1 for item in review_records if item.get("duplicate_of")
    )
    return {
        "catalog_version": GRCL9V3_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION,
        "session_id": session_id,
        "session_root": str(session_root),
        "created_at": date.today().isoformat(),
        "selector_session_ids": list(selector_session_ids),
        "source_sessions": [
            str(output_root / "sessions" / selector_session_id)
            for selector_session_id in selector_session_ids
        ],
        "review_policy": {
            "accepted": (
                "strong selector evidence with required artifacts and no legacy "
                "standalone-growth dependency"
            ),
            "strong_candidate": (
                "candidate selector evidence retained without full accepted status"
            ),
            "growth_policy": (
                "growth/front records are paper-facing only when Iteration 9 "
                "front-growth provenance selectors and telemetry are present"
            ),
            "legacy_growth_policy": (
                "older standalone growth-locus records are preserved as "
                "superseded diagnostics, not accepted motifs"
            ),
            "visual_policy": (
                "visual records support review and artifact linking; visuals never "
                "promote a record without selector evidence"
            ),
        },
        "summary": {
            "reviewed_count": len(review_records),
            "accepted_count": len(accepted),
            "strong_candidate_count": len(strong),
            "diagnostic_count": len(diagnostics),
            "superseded_count": len(superseded),
            "rejected_count": len(rejected),
            "duplicate_link_count": duplicate_link_count,
            "needs_rerun_count": 0,
            "review_status_counts": dict(sorted(status_counts.items())),
            "evidence_class_counts": dict(sorted(evidence_counts.items())),
            "accepted_growth_count": sum(
                1
                for item in accepted
                if item.get("growth_review", {}).get("has_growth_claim")
            ),
            "superseded_growth_count": len(superseded),
        },
        "accepted_motifs": accepted,
        "strong_candidate_motifs": strong,
        "diagnostic_motifs": diagnostics,
        "superseded_motifs": superseded,
        "rejected_motifs": rejected,
        "all_reviewed_records": list(review_records),
        "non_claims": [
            "GRCL-9V3 source seeds declare Morse/phenomenology preconditions, not solved outcomes",
            "catalog acceptance is selector-backed telemetry evidence, not source truth",
            "visuals are supporting evidence only",
            "legacy standalone-growth records are diagnostic after Iteration 9 semantics correction",
            "accepted growth/front records require corrected front-growth provenance",
        ],
    }


def _review_report_payload(
    *,
    session_id: str,
    selector_session_ids: tuple[str, ...],
    review_records: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    status_counts = Counter(str(item["review_status"]) for item in review_records)
    label_counts = Counter(str(item["confidence_label"]) for item in review_records)
    return {
        "catalog_version": GRCL9V3_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION,
        "session_id": session_id,
        "selector_session_ids": list(selector_session_ids),
        "review_status_counts": dict(sorted(status_counts.items())),
        "selector_confidence_counts": dict(sorted(label_counts.items())),
        "accepted_count": status_counts.get("accepted", 0),
        "strong_candidate_count": status_counts.get("strong_candidate", 0),
        "diagnostic_count": status_counts.get("diagnostic", 0),
        "superseded_count": status_counts.get(
            "superseded_by_growth_semantics_correction", 0
        ),
        "rejected_count": status_counts.get("rejected", 0),
        "duplicate_link_count": sum(
            1 for item in review_records if item.get("duplicate_of")
        ),
        "needs_rerun_count": 0,
        "superseded_records": [
            {
                "motif_id": item["motif_id"],
                "fixture_name": item["fixture_name"],
                "source_session_id": item["source_session_id"],
                "review_notes": item["review_notes"],
            }
            for item in review_records
            if item["review_status"] == "superseded_by_growth_semantics_correction"
        ],
        "rejections": [
            {
                "motif_id": item["motif_id"],
                "fixture_name": item["fixture_name"],
                "failure_notes": item["failure_notes"],
                "review_notes": item["review_notes"],
            }
            for item in review_records
            if item["review_status"] == "rejected"
        ],
    }


def _summary_markdown(catalog: Mapping[str, Any]) -> str:
    summary = catalog["summary"]
    lines = [
        "# Reviewed GRCL-9V3 Lowered-Source Motif Catalog",
        "",
        f"Catalog version: `{catalog['catalog_version']}`",
        f"Session: `{catalog['session_id']}`",
        f"Selector sessions: {', '.join(f'`{item}`' for item in catalog['selector_session_ids'])}",
        "",
        "## Summary",
        "",
        f"- Accepted motifs: {summary['accepted_count']}",
        f"- Strong candidates: {summary['strong_candidate_count']}",
        f"- Diagnostics: {summary['diagnostic_count']}",
        f"- Superseded legacy growth records: {summary['superseded_count']}",
        f"- Rejected records: {summary['rejected_count']}",
        f"- Duplicate links: {summary['duplicate_link_count']}",
        f"- Needs-rerun records: {summary['needs_rerun_count']}",
        f"- Accepted growth/front motifs: {summary['accepted_growth_count']}",
        "",
        "## Accepted Motifs",
        "",
        "| Motif | Fixture | Source | Evidence Class | Events | Duplicate Of |",
        "|---|---|---|---|---:|---|",
    ]
    for motif in catalog["accepted_motifs"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{motif['motif_id']}`",
                    f"`{motif['fixture_name']}`",
                    f"`{motif['source_session_id']}`",
                    f"`{motif['evidence_class']}`",
                    str(sum(int(v) for v in motif.get("event_counts_by_kind", {}).values())),
                    f"`{motif['duplicate_of']}`" if motif.get("duplicate_of") else "",
                ]
            )
            + " |"
        )
    if catalog["strong_candidate_motifs"]:
        lines.extend(
            [
                "",
                "## Strong Candidates",
                "",
                "| Motif | Fixture | Reason |",
                "|---|---|---|",
            ]
        )
        for motif in catalog["strong_candidate_motifs"]:
            lines.append(
                f"| `{motif['motif_id']}` | `{motif['fixture_name']}` | "
                f"{'; '.join(motif.get('review_notes', ())) or 'candidate evidence'} |"
            )
    if catalog["superseded_motifs"]:
        lines.extend(
            [
                "",
                "## Superseded Legacy Growth",
                "",
                "| Motif | Fixture | Source | Status |",
                "|---|---|---|---|",
            ]
        )
        for motif in catalog["superseded_motifs"]:
            lines.append(
                f"| `{motif['motif_id']}` | `{motif['fixture_name']}` | "
                f"`{motif['source_session_id']}` | "
                "`superseded_by_growth_semantics_correction` |"
            )
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Source seeds declare GRCL/Morse preconditions, not solved runtime outcomes.",
            "- Selector telemetry is the primary evidence; visuals are supporting only.",
            "- Legacy standalone-growth records remain replayable diagnostics, not accepted paper-facing growth evidence.",
            "- Accepted growth/front records require Iteration 9 corrected front-growth provenance.",
            "",
        ]
    )
    return "\n".join(lines)


def _session_manifest(
    *,
    session_id: str,
    catalog_path: Path,
    review_report_path: Path,
    summary_path: Path,
    selector_session_ids: tuple[str, ...],
    output_root: Path,
) -> Mapping[str, Any]:
    command = (
        "PYTHONPATH=src python -m pygrc.telemetry.grcl9v3_lowered_motif_catalog "
        f"--session-id {session_id} "
        + " ".join(
            f"--selector-session-id {selector_session_id}"
            for selector_session_id in selector_session_ids
        )
        + f" --output-root {output_root}"
    )
    return {
        "session_id": session_id,
        "session_kind": "grcl9v3_reviewed_lowered_motif_catalog",
        "catalog_version": GRCL9V3_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION,
        "family": "grcl9v3",
        "iteration": "I10_reviewed_lowered_source_catalog",
        "selector_session_ids": list(selector_session_ids),
        "source_reference": "implementation/GRCL-9V3-ImplementationPlan.md",
        "replay_command": command,
        "input_paths": [
            str(output_root / "sessions" / selector_session_id)
            for selector_session_id in selector_session_ids
        ],
        "output_paths": [
            str(catalog_path),
            str(review_report_path),
            str(summary_path),
        ],
    }


def _write_readme(root: Path, catalog: Mapping[str, Any]) -> None:
    summary = catalog["summary"]
    lines = [
        f"# {catalog['session_id']}. GRCL-9V3 Reviewed Lowered-Source Catalog",
        "",
        "Status: `completed`",
        "",
        "Primary artifacts:",
        "",
        "- `reviewed_grcl9v3_lowered_motif_catalog.json`",
        "- `reports/reviewed_grcl9v3_lowered_motif_catalog_report.json`",
        "- `reports/reviewed_grcl9v3_lowered_motif_catalog_summary.md`",
        "",
        "Summary:",
        "",
        f"- accepted: `{summary['accepted_count']}`",
        f"- strong candidates: `{summary['strong_candidate_count']}`",
        f"- superseded legacy growth: `{summary['superseded_count']}`",
        f"- rejected: `{summary['rejected_count']}`",
        "",
    ]
    _write_text(root / "README.md", "\n".join(lines))


def _write_experimental_log(path: Path, catalog: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = (
        f"| {catalog['session_id']} | reviewed_lowered_source_catalog | "
        f"{catalog['summary']['accepted_count']} accepted, "
        f"{catalog['summary']['strong_candidate_count']} strong candidates, "
        f"{catalog['summary']['superseded_count']} superseded | "
        f"{catalog['session_root']} |\n"
    )
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if row in text:
            return
        path.write_text(text.rstrip() + "\n" + row, encoding="utf-8")
        return
    path.write_text(
        "# GRCL-9V3 Lowering Experimental Log\n\n"
        "| Session | Kind | Summary | Path |\n"
        "|---|---|---|---|\n"
        + row,
        encoding="utf-8",
    )


def _get_path(payload: Mapping[str, Any], path: str, default: Any = None) -> Any:
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, Mapping) and part in current:
            current = current[part]
        else:
            return default
    return current


def _motif_id(selector_session_id: str, fixture_name: str) -> str:
    return (
        f"grcl9v3-lowered-{selector_session_id.lower()}-"
        f"{fixture_name.replace('_', '-')}"
    )


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", default="S0072")
    parser.add_argument("--output-root", default=str(GRCL9V3_REPLAY_ROOT))
    parser.add_argument(
        "--selector-session-id",
        action="append",
        dest="selector_session_ids",
        default=None,
    )
    args = parser.parse_args(argv)
    session = run_grcl9v3_reviewed_lowered_motif_catalog(
        session_id=args.session_id,
        output_root=args.output_root,
        selector_session_ids=tuple(
            args.selector_session_ids or DEFAULT_GRCL9V3_CATALOG_SELECTOR_SESSIONS
        ),
    )
    print(json.dumps(session.to_mapping(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())


__all__ = [
    "DEFAULT_GRCL9V3_CATALOG_SELECTOR_SESSIONS",
    "DEFAULT_GRCL9V3_CATALOG_VISUAL_SESSIONS",
    "GRCL9V3_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION",
    "GRCL9V3ReviewedLoweredMotifCatalogSession",
    "run_grcl9v3_reviewed_lowered_motif_catalog",
]
