"""Reviewed GRCL-9 lowered motif catalog generation."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
import hashlib
import json
from pathlib import Path
from typing import Any

from .grcl9_replay import GRCL9_REPLAY_ROOT, LEGACY_GROWTH_SOURCE_MODES


GRCL9_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION = (
    "grcl9_reviewed_lowered_motif_catalog_v1"
)
DEFAULT_GRCL9_CATALOG_SOURCE_SESSIONS = ("S0006", "S0007")
_COLLAPSE_DIAGNOSTIC_SELECTOR_IDS = frozenset(
    {
        "runtime_collapse_like_ambiguous",
        "runtime_collapse_like_classification",
        "runtime_collapse_like_observed",
        "runtime_collapse_like_long_window",
        "structural_only",
    }
)


@dataclass(frozen=True)
class GRCL9ReviewedLoweredMotifCatalogSession:
    """Result from a reviewed GRCL-9 lowered motif catalog run."""

    session_id: str
    session_root: Path
    catalog_path: Path
    review_report_path: Path
    summary_path: Path
    accepted_count: int
    rejected_count: int
    duplicate_link_count: int

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "session_root": str(self.session_root),
            "catalog_path": str(self.catalog_path),
            "review_report_path": str(self.review_report_path),
            "summary_path": str(self.summary_path),
            "accepted_count": self.accepted_count,
            "rejected_count": self.rejected_count,
            "duplicate_link_count": self.duplicate_link_count,
        }


def run_grcl9_reviewed_lowered_motif_catalog(
    *,
    session_id: str = "S0008",
    source_session_ids: Sequence[str] = DEFAULT_GRCL9_CATALOG_SOURCE_SESSIONS,
    output_root: str | Path = GRCL9_REPLAY_ROOT,
    force_legacy_growth: bool = False,
) -> GRCL9ReviewedLoweredMotifCatalogSession:
    """Promote selector-backed GRCL-9 lowering lanes into a reviewed catalog."""

    if not session_id.startswith("S"):
        raise ValueError("session_id must be an S-prefixed replay session id")
    if not source_session_ids:
        raise ValueError("source_session_ids must not be empty")

    root = Path(output_root)
    session_root = root / "sessions" / session_id
    reports_root = session_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    source_sessions = [_load_source_session(root / "sessions" / item) for item in source_session_ids]
    legacy_source_session_ids = tuple(
        str(source_session["manifest"].get("session_id", source_session["session_root"].name))
        for source_session in source_sessions
        if _source_session_uses_legacy_growth(source_session)
    )
    if legacy_source_session_ids and not force_legacy_growth:
        raise ValueError(
            "reviewed GRCL-9 catalog refuses legacy broad-growth source sessions "
            f"{', '.join(legacy_source_session_ids)}. Use --force-legacy-growth "
            "only to rebuild historical diagnostic catalogs; legacy growth "
            "records must not be used as corrected evidence."
        )
    accepted, rejected = _review_source_sessions(source_sessions)
    _apply_duplicate_links(accepted)

    duplicate_links = [
        {
            "motif_id": motif["motif_id"],
            "duplicate_of": motif["duplicate_of"],
            "duplicate_group_id": motif["duplicate_group_id"],
        }
        for motif in accepted
        if motif.get("duplicate_of")
    ]
    catalog = _catalog_payload(
        session_id=session_id,
        session_root=session_root,
        output_root=root,
        source_session_ids=tuple(source_session_ids),
        accepted=accepted,
        rejected=rejected,
        duplicate_links=duplicate_links,
        force_legacy_growth=force_legacy_growth,
        legacy_source_session_ids=legacy_source_session_ids,
    )
    report = _review_report_payload(
        session_id=session_id,
        source_session_ids=tuple(source_session_ids),
        accepted=accepted,
        rejected=rejected,
        duplicate_links=duplicate_links,
        force_legacy_growth=force_legacy_growth,
        legacy_source_session_ids=legacy_source_session_ids,
    )

    catalog_path = session_root / "reviewed_grcl9_lowered_motif_catalog.json"
    review_report_path = reports_root / "reviewed_grcl9_lowered_motif_catalog_report.json"
    summary_path = reports_root / "reviewed_grcl9_lowered_motif_catalog_summary.md"
    _write_json(catalog_path, catalog)
    _write_json(review_report_path, report)
    _write_text(summary_path, _summary_markdown(catalog))
    return GRCL9ReviewedLoweredMotifCatalogSession(
        session_id=session_id,
        session_root=session_root,
        catalog_path=catalog_path,
        review_report_path=review_report_path,
        summary_path=summary_path,
        accepted_count=len(accepted),
        rejected_count=len(rejected),
        duplicate_link_count=len(duplicate_links),
    )


def _load_source_session(session_root: Path) -> Mapping[str, Any]:
    manifest_path = session_root / "session_manifest.json"
    visual_manifest_path = session_root / "visualizations" / "visualization_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing GRCL-9 session manifest: {manifest_path}")
    if not visual_manifest_path.exists():
        raise FileNotFoundError(f"missing GRCL-9 visualization manifest: {visual_manifest_path}")
    return {
        "session_root": session_root,
        "manifest": _read_json(manifest_path),
        "visualization_manifest": _read_json(visual_manifest_path),
    }


def _source_session_uses_legacy_growth(source_session: Mapping[str, Any]) -> bool:
    manifest = source_session["manifest"]
    if str(manifest.get("source_mode", "")) in LEGACY_GROWTH_SOURCE_MODES:
        return True
    for lane in manifest.get("lanes", ()):
        if not isinstance(lane, Mapping):
            continue
        if bool(lane.get("legacy_broad_growth_non_evidence", False)):
            return True
    visualization_manifest = source_session["visualization_manifest"]
    for lane in visualization_manifest.get("lanes", ()):
        if not isinstance(lane, Mapping):
            continue
        if bool(lane.get("legacy_broad_growth_non_evidence", False)):
            return True
    return False


def _review_source_sessions(
    source_sessions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for source_session in source_sessions:
        session_root = Path(source_session["session_root"])
        manifest = source_session["manifest"]
        session_id = str(manifest["session_id"])
        phase_records_by_fixture = _phase_records_by_fixture(session_root)
        visuals_by_fixture = {
            str(item["fixture_name"]): item
            for item in source_session["visualization_manifest"].get("lanes", ())
        }
        for lane in manifest.get("lanes", ()):
            review = _review_lane(
                session_id=session_id,
                session_root=session_root,
                lane=lane,
                visual=visuals_by_fixture.get(str(lane.get("fixture_name")), {}),
                phase_record=phase_records_by_fixture.get(str(lane.get("fixture_name")), {}),
            )
            if review["review_status"] == "accepted":
                accepted.append(review)
            else:
                rejected.append(review)
    return accepted, rejected


def _review_lane(
    *,
    session_id: str,
    session_root: Path,
    lane: Mapping[str, Any],
    visual: Mapping[str, Any],
    phase_record: Mapping[str, Any],
) -> dict[str, Any]:
    fixture_name = str(lane["fixture_name"])
    selector_report_path = Path(str(lane["selector_report_path"]))
    source_fixture_path = Path(str(lane["source_fixture_path"]))
    lowered_state_path = Path(str(lane["lowered_state_path"]))
    artifact_root = Path(str(lane["artifact_root"]))
    example_path = session_root / "grcl_landscape_examples" / f"{fixture_name}.json"
    run_summary_path = artifact_root / "telemetry" / "run_summary.json"
    events_path = artifact_root / "telemetry" / "events.jsonl"
    steps_path = artifact_root / "telemetry" / "steps.jsonl"
    checkpoint_index_path = artifact_root / "telemetry" / "graph_checkpoints" / "index.json"

    required_paths = {
        "grcl_landscape_example": example_path,
        "compiled_source": source_fixture_path,
        "lowered_state": lowered_state_path,
        "selector_report": selector_report_path,
        "telemetry_run_summary": run_summary_path,
        "telemetry_events": events_path,
        "telemetry_steps": steps_path,
        "graph_checkpoint_index": checkpoint_index_path,
    }
    missing = [name for name, path in required_paths.items() if not path.exists()]
    if not visual:
        missing.append("visualization_manifest_entry")
    selector_report = _read_json(selector_report_path) if selector_report_path.exists() else {}
    source = _read_json(source_fixture_path) if source_fixture_path.exists() else {}
    lowered = _read_json(lowered_state_path) if lowered_state_path.exists() else {}

    artifact_links = _artifact_links(
        session_root=session_root,
        fixture_name=fixture_name,
        source=source,
        required_paths=required_paths,
        visual=visual,
    )
    non_claims = tuple(str(item) for item in source.get("non_claims", ()))
    motif_registry = lowered.get("cached_quantities", {}).get("grcl9_motif_registry", {})
    motif_roles = sorted(
        {
            str(role)
            for item in motif_registry.values()
            for role in item.get("motif_roles", ())
        }
    )
    source_construct_kinds = tuple(
        str(item.get("construct_kind", ""))
        for item in source.get("constructs", ())
        if item.get("construct_kind")
    )
    selector_status = str(selector_report.get("status", lane.get("selector_status", "")))
    selector_results = list(selector_report.get("selector_results", ()))
    failure_notes = list(selector_report.get("failure_notes", ()))
    if missing:
        failure_notes.append("missing required artifacts: " + ", ".join(missing))
    if selector_status != "passed":
        failure_notes.append(f"selector status is {selector_status!r}")
    review_status = "accepted" if not missing and selector_status == "passed" else "rejected"
    entry = {
        "motif_id": f"grcl9_lowered_{session_id.lower()}_{fixture_name}",
        "review_status": review_status,
        "source_session_id": session_id,
        "evidence_class": (
            "composing_cells_seed" if fixture_name.startswith("cell_") else "mechanism_probe"
        ),
        "fixture_name": fixture_name,
        "manifest_entry_id": str(lane["manifest_entry_id"]),
        "run_id": str(lane["run_id"]),
        "requested_steps": int(lane["requested_steps"]),
        "event_count": int(lane["event_count"]),
        "event_counts_by_kind": dict(lane.get("event_counts_by_kind", {})),
        "selector_status": selector_status,
        "selector_results": selector_results,
        "collapse_diagnostic": _collapse_diagnostic(
            selector_results=selector_results,
            phase_record=phase_record,
            session_root=session_root,
        ),
        "failure_notes": failure_notes,
        "artifact_links": artifact_links,
        "source_construct_kinds": list(source_construct_kinds),
        "source_term_kinds": _source_term_kinds(source),
        "motif_registry": motif_registry,
        "motif_roles": motif_roles,
        "bridge_edge_count": int(visual.get("bridge_edge_count", 0)),
        "connected": bool(visual.get("connected", False)),
        "non_claims": list(non_claims),
        "duplicate_group_id": _duplicate_group_id(
            manifest_entry_id=str(lane["manifest_entry_id"]),
            source_construct_kinds=source_construct_kinds,
            selector_ids=tuple(source.get("expected_selector_ids", ())),
            motif_roles=tuple(motif_roles),
        ),
        "duplicate_of": None,
    }
    return entry


def _phase_records_by_fixture(session_root: Path) -> dict[str, Mapping[str, Any]]:
    summary_path = session_root / "reports" / "phase_diagram_summary.json"
    if not summary_path.exists():
        return {}
    summary = _read_json(summary_path)
    records: dict[str, Mapping[str, Any]] = {}
    for item in summary.get("lanes", ()):
        if isinstance(item, Mapping) and item.get("fixture_name"):
            records[str(item["fixture_name"])] = item
    return records


def _collapse_diagnostic(
    *,
    selector_results: Sequence[Mapping[str, Any]],
    phase_record: Mapping[str, Any],
    session_root: Path,
) -> Mapping[str, Any]:
    collapse_results = [
        result
        for result in selector_results
        if str(result.get("selector_id", "")) in _COLLAPSE_DIAGNOSTIC_SELECTOR_IDS
    ]
    if not collapse_results:
        return {
            "status": "not_applicable",
            "accepted_surface": False,
            "selector_ids": [],
        }

    observed_values = [
        result.get("observed_value")
        for result in collapse_results
        if isinstance(result.get("observed_value"), Mapping)
    ]
    primary = observed_values[0] if observed_values else {}
    classification = str(primary.get("classification", "unknown"))
    phase_context = _phase_context(phase_record, session_root=session_root)
    return {
        "status": _collapse_diagnostic_status(classification),
        "accepted_surface": True,
        "selector_ids": [str(result.get("selector_id", "")) for result in collapse_results],
        "selector_evidence_statuses": sorted(
            {str(result.get("evidence_status", "")) for result in collapse_results}
        ),
        "classification": classification,
        "lost_source_sink_roles": list(primary.get("lost_source_sink_roles", ())),
        "final_source_sink_roles": list(primary.get("final_source_sink_roles", ())),
        "residual_collapsing_basin_sink_roles": list(
            primary.get("residual_collapsing_basin_sink_roles", ())
        ),
        "target_selection_policy": str(primary.get("target_selection_policy", "")),
        "target_selection_kind": str(primary.get("target_selection_kind", "")),
        "target_selected_node_id": primary.get("target_selected_node_id"),
        "source_basin_a_node_count": len(tuple(primary.get("source_basin_a_node_ids", ()))),
        "source_basin_b_node_count": len(tuple(primary.get("source_basin_b_node_ids", ()))),
        "identity_fission_candidate_count": int(
            primary.get("identity_fission_candidate_count", 0)
        ),
        "identity_fission_confirmed_count": int(
            primary.get("identity_fission_confirmed_count", 0)
        ),
        "phase_context": phase_context,
        "non_claims": [
            "collapse_diagnostic is selector-backed and diagnostic-only",
            "no GRC9 collapse event kind or collapse runtime equation is introduced",
            "source-declared sink-role loss is not GRCV3 collapse semantics",
        ],
    }


def _collapse_diagnostic_status(classification: str) -> str:
    if classification == "runtime_collapse_like_observed":
        return "runtime_collapse_like_diagnostic"
    if classification == "ambiguous":
        return "ambiguous_collapse_like_diagnostic"
    if classification == "structural_only":
        return "structural_only_control"
    return "unknown"


def _phase_context(
    phase_record: Mapping[str, Any],
    *,
    session_root: Path,
) -> Mapping[str, Any] | None:
    if not phase_record:
        return None
    return {
        "basin_regime": str(phase_record.get("basin_regime", "")),
        "growth_regime": str(phase_record.get("growth_regime", "")),
        "event_amplification_class": str(phase_record.get("event_amplification_class", "")),
        "module_size_observed": phase_record.get("module_size_observed"),
        "event_count_total": int(phase_record.get("event_count_total", 0)),
        "phase_diagram_summary": str(session_root / "reports" / "phase_diagram_summary.json"),
        "phase_diagram_report": str(session_root / "reports" / "phase_diagram_summary.md"),
        "phase_diagram_visual_index": str(
            session_root / "visualizations" / "phase_diagram_visual_index.md"
        ),
    }


def _artifact_links(
    *,
    session_root: Path,
    fixture_name: str,
    source: Mapping[str, Any],
    required_paths: Mapping[str, Path],
    visual: Mapping[str, Any],
) -> Mapping[str, Any]:
    seed_reference = (
        source.get("compiled_source_provenance", {}).get("source_seed_reference")
        if isinstance(source.get("compiled_source_provenance"), Mapping)
        else None
    )
    seed_path = None
    if seed_reference:
        candidate = session_root / "grcl_landscape_seeds" / Path(str(seed_reference)).name
        seed_path = str(candidate)
    return {
        "source_seed": seed_path,
        "grcl_landscape_example": str(required_paths["grcl_landscape_example"]),
        "compiled_source": str(required_paths["compiled_source"]),
        "lowered_state": str(required_paths["lowered_state"]),
        "selector_report": str(required_paths["selector_report"]),
        "telemetry": {
            "run_summary": str(required_paths["telemetry_run_summary"]),
            "events": str(required_paths["telemetry_events"]),
            "steps": str(required_paths["telemetry_steps"]),
        },
        "graph_checkpoints": {
            "index": str(required_paths["graph_checkpoint_index"]),
        },
        "visualization": {
            "panel": str(visual.get("boundary_panel_path", "")),
            "overlay": str(visual.get("grcl9_overlay_path", "")),
            "overlay_summary": str(visual.get("grcl9_overlay_summary_path", "")),
            "graph_sequence": str(visual.get("graph_sequence_path", "")),
            "event_timeline": str(visual.get("event_timeline_path", "")),
            "trajectory": str(visual.get("trajectory_path", "")),
            "index": str(session_root / "visualizations" / "index.md"),
        },
    }


def _source_term_kinds(source: Mapping[str, Any]) -> list[str]:
    provenance = source.get("compiled_source_provenance", {})
    if not isinstance(provenance, Mapping):
        return []
    terms = provenance.get("source_terms", ())
    return sorted({str(item.get("term_kind")) for item in terms if isinstance(item, Mapping)})


def _duplicate_group_id(
    *,
    manifest_entry_id: str,
    source_construct_kinds: Sequence[str],
    selector_ids: Sequence[str],
    motif_roles: Sequence[str],
) -> str:
    roles_digest = hashlib.sha256(
        json.dumps(list(motif_roles), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:12]
    return "dup_" + "_".join(
        [
            manifest_entry_id,
            "constructs_" + "_".join(source_construct_kinds),
            "selectors_" + "_".join(selector_ids),
            "roles_" + roles_digest,
        ]
    )


def _apply_duplicate_links(accepted: list[dict[str, Any]]) -> None:
    first_by_group: dict[str, str] = {}
    for motif in accepted:
        group_id = str(motif["duplicate_group_id"])
        first = first_by_group.setdefault(group_id, str(motif["motif_id"]))
        if first != motif["motif_id"]:
            motif["duplicate_of"] = first


def _catalog_payload(
    *,
    session_id: str,
    session_root: Path,
    output_root: Path,
    source_session_ids: tuple[str, ...],
    accepted: Sequence[Mapping[str, Any]],
    rejected: Sequence[Mapping[str, Any]],
    duplicate_links: Sequence[Mapping[str, Any]],
    force_legacy_growth: bool,
    legacy_source_session_ids: Sequence[str],
) -> Mapping[str, Any]:
    evidence_counts = Counter(str(item["evidence_class"]) for item in accepted)
    manifest_counts = Counter(str(item["manifest_entry_id"]) for item in accepted)
    collapse_diagnostics = [
        diagnostic
        for item in accepted
        if isinstance((diagnostic := item.get("collapse_diagnostic")), Mapping)
        and diagnostic.get("status") != "not_applicable"
    ]
    collapse_status_counts = Counter(
        str(item.get("status", "unknown")) for item in collapse_diagnostics
    )
    collapse_classification_counts = Counter(
        str(item.get("classification", "unknown")) for item in collapse_diagnostics
    )
    return {
        "catalog_version": GRCL9_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION,
        "session_id": session_id,
        "session_root": str(session_root),
        "created_at": date.today().isoformat(),
        "source_session_ids": list(source_session_ids),
        "source_sessions": [
            str(output_root / "sessions" / source_session_id)
            for source_session_id in source_session_ids
        ],
        "force_legacy_growth": force_legacy_growth,
        "legacy_source_session_ids": list(legacy_source_session_ids),
        "legacy_growth_guard": (
            "forced_historical_catalog_rebuild_non_evidence"
            if legacy_source_session_ids and force_legacy_growth
            else "corrected_or_non_growth_sources_only"
        ),
        "review_policy": {
            "required_status": "selector_status == passed",
            "required_artifacts": [
                "grcl_landscape_example",
                "compiled_source",
                "lowered_state",
                "selector_report",
                "telemetry_run_summary",
                "telemetry_events",
                "telemetry_steps",
                "graph_checkpoint_index",
                "visualization_manifest_entry",
            ],
            "duplicate_policy": (
                "structural grouping by manifest entry, source constructs, "
                "selector ids, and motif roles; duplicates are linked, not dropped"
            ),
            "collapse_policy": (
                "collapse-like observations are diagnostic-only selector surfaces; "
                "the catalog does not introduce a GRC9 collapse event or runtime equation"
            ),
            "legacy_growth_policy": (
                "legacy_any_inactive_port sources are refused unless "
                "--force-legacy-growth is supplied, and forced outputs are "
                "historical diagnostics rather than corrected growth evidence"
            ),
        },
        "summary": {
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "duplicate_link_count": len(duplicate_links),
            "accepted_by_evidence_class": dict(sorted(evidence_counts.items())),
            "accepted_by_manifest_entry": dict(sorted(manifest_counts.items())),
            "collapse_diagnostic_count": len(collapse_diagnostics),
            "collapse_diagnostic_status_counts": dict(
                sorted(collapse_status_counts.items())
            ),
            "collapse_diagnostic_classification_counts": dict(
                sorted(collapse_classification_counts.items())
            ),
        },
        "accepted_motifs": list(accepted),
        "rejected_motifs": list(rejected),
        "duplicate_links": list(duplicate_links),
        "non_claims": [
            "GRCL-9 remains lowering-only",
            "catalog acceptance is selector-backed telemetry evidence, not source truth",
            "collapse diagnostics are source-role loss observations, not new GRC9 collapse semantics",
            "no GRCV3 hierarchy, Lorentzian causal layer, or observer-local semantics are claimed",
        ],
    }


def _review_report_payload(
    *,
    session_id: str,
    source_session_ids: tuple[str, ...],
    accepted: Sequence[Mapping[str, Any]],
    rejected: Sequence[Mapping[str, Any]],
    duplicate_links: Sequence[Mapping[str, Any]],
    force_legacy_growth: bool,
    legacy_source_session_ids: Sequence[str],
) -> Mapping[str, Any]:
    return {
        "catalog_version": GRCL9_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION,
        "session_id": session_id,
        "source_session_ids": list(source_session_ids),
        "force_legacy_growth": force_legacy_growth,
        "legacy_source_session_ids": list(legacy_source_session_ids),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "duplicate_link_count": len(duplicate_links),
        "selector_status_counts": dict(
            sorted(Counter(str(item.get("selector_status")) for item in accepted).items())
        ),
        "collapse_diagnostic_status_counts": dict(
            sorted(
                Counter(
                    str(diagnostic.get("status", "unknown"))
                    for item in accepted
                    if isinstance((diagnostic := item.get("collapse_diagnostic")), Mapping)
                    and diagnostic.get("status") != "not_applicable"
                ).items()
            )
        ),
        "rejections": [
            {
                "motif_id": item["motif_id"],
                "fixture_name": item["fixture_name"],
                "failure_notes": item["failure_notes"],
            }
            for item in rejected
        ],
        "duplicate_links": list(duplicate_links),
    }


def _summary_markdown(catalog: Mapping[str, Any]) -> str:
    summary = catalog["summary"]
    lines = [
        "# Reviewed GRCL-9 Lowered Motif Catalog",
        "",
        f"Catalog version: `{catalog['catalog_version']}`",
        f"Session: `{catalog['session_id']}`",
        f"Source sessions: {', '.join(f'`{item}`' for item in catalog['source_session_ids'])}",
        "",
        "## Summary",
        "",
        f"- Accepted motifs: {summary['accepted_count']}",
        f"- Rejected motifs: {summary['rejected_count']}",
        f"- Duplicate links: {summary['duplicate_link_count']}",
        f"- Collapse diagnostics: {summary.get('collapse_diagnostic_count', 0)}",
        "",
    ]
    collapse_motifs = [
        motif
        for motif in catalog["accepted_motifs"]
        if motif.get("collapse_diagnostic", {}).get("status") != "not_applicable"
    ]
    if collapse_motifs:
        lines.extend(
            [
                "## Collapse Diagnostics",
                "",
                "| Motif | Fixture | Status | Classification | Lost Roles | Phase |",
                "|---|---|---|---|---|---|",
            ]
        )
        for motif in collapse_motifs:
            diagnostic = motif["collapse_diagnostic"]
            phase = diagnostic.get("phase_context") or {}
            phase_label = ""
            if phase:
                phase_label = (
                    f"{phase.get('basin_regime', '')}/"
                    f"{phase.get('growth_regime', '')}/"
                    f"{phase.get('event_amplification_class', '')}"
                )
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{motif['motif_id']}`",
                        f"`{motif['fixture_name']}`",
                        f"`{diagnostic.get('status', '')}`",
                        f"`{diagnostic.get('classification', '')}`",
                        ", ".join(
                            f"`{item}`"
                            for item in diagnostic.get("lost_source_sink_roles", ())
                        ),
                        f"`{phase_label}`" if phase_label else "",
                    ]
                )
                + " |"
            )
        lines.append("")
    lines.extend(
        [
            "## Accepted Motifs",
            "",
            "| Motif | Source Session | Evidence Class | Fixture | Manifest Entry | Events | Duplicate Of |",
            "|---|---|---|---|---|---:|---|",
        ]
    )
    for motif in catalog["accepted_motifs"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{motif['motif_id']}`",
                    f"`{motif['source_session_id']}`",
                    f"`{motif['evidence_class']}`",
                    f"`{motif['fixture_name']}`",
                    f"`{motif['manifest_entry_id']}`",
                    str(motif["event_count"]),
                    f"`{motif['duplicate_of']}`" if motif.get("duplicate_of") else "",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- GRCL-9 remains lowering-only.",
            "- Accepted motifs are selector-backed telemetry evidence, not source-level event claims.",
            "- Collapse diagnostics record source-role loss from existing telemetry/checkpoints; they are not GRC9 collapse events.",
            "- The catalog does not add GRCV3 hierarchy, Lorentzian, or observer-local semantics.",
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", default="S0008")
    parser.add_argument("--output-root", default=str(GRCL9_REPLAY_ROOT))
    parser.add_argument(
        "--source-session-id",
        action="append",
        dest="source_session_ids",
        default=None,
    )
    parser.add_argument(
        "--force-legacy-growth",
        action="store_true",
        help=(
            "Allow rebuilding historical catalogs from legacy broad-growth "
            "sessions. Forced outputs are diagnostic non-evidence."
        ),
    )
    args = parser.parse_args(argv)
    session = run_grcl9_reviewed_lowered_motif_catalog(
        session_id=args.session_id,
        output_root=args.output_root,
        source_session_ids=tuple(args.source_session_ids or DEFAULT_GRCL9_CATALOG_SOURCE_SESSIONS),
        force_legacy_growth=args.force_legacy_growth,
    )
    print(json.dumps(session.to_mapping(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())


__all__ = [
    "DEFAULT_GRCL9_CATALOG_SOURCE_SESSIONS",
    "GRCL9_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION",
    "GRCL9ReviewedLoweredMotifCatalogSession",
    "run_grcl9_reviewed_lowered_motif_catalog",
]
