"""Source-language planning handoff for reviewed GRC9V3 runtime motifs."""

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


GRC9V3_SOURCE_HANDOFF_VERSION = "grc9v3_source_handoff_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9v3/phenomenology_discovery/sessions")
EXPERIMENTAL_LOG_PATH = Path("outputs/grc9v3/phenomenology_discovery/ExperimentalLog.md")
_HANDOFF_BOUNDARY = (
    "This handoff does not implement GRCL/source lowering and does not claim "
    "that any GRC9V3 runtime motif is already a source-language construct."
)
_BASE_NON_CLAIMS = (
    "no_grcl9_source_lowering_claim",
    "no_source_language_construct_claim",
    "no_lorentzian_causal_layer_claim",
    "no_visual_only_promotion",
)
_SOURCE_LIFECYCLE_CATEGORIES = {"simple_lifecycle_motif", "lifecycle_motif"}
_RUNTIME_ONLY_PHENOMENA = {
    "budget_preservation",
    "coarse_cache_invalidation",
    "hessian_backend_comparison",
}


@dataclass(frozen=True)
class GRC9V3SourceHandoffSession:
    session_id: str
    source_catalog_session_id: str
    source_catalog_path: str
    handoff_json_path: str
    handoff_markdown_path: str
    report_path: str
    entries: tuple[Mapping[str, Any], ...]

    def to_mapping(self) -> Mapping[str, Any]:
        disposition_counts = Counter(str(entry.get("disposition", "")) for entry in self.entries)
        return {
            "session_id": self.session_id,
            "version": GRC9V3_SOURCE_HANDOFF_VERSION,
            "source_catalog_session_id": self.source_catalog_session_id,
            "source_catalog_path": self.source_catalog_path,
            "handoff_json_path": self.handoff_json_path,
            "handoff_markdown_path": self.handoff_markdown_path,
            "report_path": self.report_path,
            "motif_count": len(self.entries),
            "source_expression_candidate_count": disposition_counts.get(
                "source_expression_candidate",
                0,
            ),
            "requires_new_source_vocabulary_count": disposition_counts.get(
                "requires_new_source_vocabulary",
                0,
            ),
            "runtime_only_count": disposition_counts.get("runtime_only", 0),
            "disposition_counts": dict(sorted(disposition_counts.items())),
        }


def run_grc9v3_source_handoff(
    *,
    session_id: str = "S0014",
    source_catalog_session_id: str = "S0013",
    session_root: str | Path | None = None,
    source_catalog_path: str | Path | None = None,
    update_experimental_log: bool = True,
) -> GRC9V3SourceHandoffSession:
    """Write a planning handoff from reviewed GRC9V3 motifs to later source work."""

    for value in (session_id, source_catalog_session_id):
        if not is_session_id(value):
            raise ValueError("session ids must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    catalog_path = (
        Path(source_catalog_path)
        if source_catalog_path is not None
        else DISCOVERY_SESSION_ROOT / source_catalog_session_id / "expanded_motif_catalog.json"
    )
    catalog = _read_required_json(catalog_path, "expanded motif catalog")
    records = tuple(
        record for record in catalog.get("records", ()) if isinstance(record, Mapping)
    )
    entries = tuple(_handoff_entry(record) for record in records)
    payload = {
        "version": GRC9V3_SOURCE_HANDOFF_VERSION,
        "session_id": session_id,
        "source_catalog_session_id": source_catalog_session_id,
        "source_catalog_path": str(catalog_path),
        "boundary_statement": _HANDOFF_BOUNDARY,
        "entries": list(entries),
        "source_expression_candidates": [
            entry
            for entry in entries
            if entry["disposition"] == "source_expression_candidate"
        ],
        "requires_new_source_vocabulary": [
            entry
            for entry in entries
            if entry["disposition"] == "requires_new_source_vocabulary"
        ],
        "runtime_only": [
            entry for entry in entries if entry["disposition"] == "runtime_only"
        ],
        "non_claims": sorted(
            set(_BASE_NON_CLAIMS)
            | {
                claim
                for entry in entries
                for claim in tuple(entry.get("explicit_non_claims", ()))
            }
        ),
    }
    json_path = root / "source_language_handoff.json"
    markdown_path = root / "source_language_handoff.md"
    report_path = reports_root / "source_language_handoff_report.json"
    session = GRC9V3SourceHandoffSession(
        session_id=session_id,
        source_catalog_session_id=source_catalog_session_id,
        source_catalog_path=str(catalog_path),
        handoff_json_path=str(json_path),
        handoff_markdown_path=str(markdown_path),
        report_path=str(report_path),
        entries=entries,
    )
    _write_json(json_path, payload)
    _write_text(markdown_path, _markdown_handoff(payload, session))
    _write_json(report_path, session.to_mapping())
    _write_json(root / "session_manifest.json", _session_manifest(session))
    _write_summary_markdown(reports_root / "source_language_handoff_summary.md", session)
    _write_readme(root, session)
    if update_experimental_log and session_root is None:
        _append_experimental_log(session)
    return session


def _handoff_entry(record: Mapping[str, Any]) -> Mapping[str, Any]:
    disposition, construct_hint, vocabulary_needs, notes = _classify_record(record)
    telemetry_root = str(record.get("telemetry_artifact_root", ""))
    return {
        "motif_id": str(record.get("motif_id", "")),
        "lane_name": str(record.get("lane_name", "")),
        "phenomenon": str(record.get("phenomenon", "")),
        "profile": str(record.get("profile", "")),
        "review_status": str(record.get("review_status", "")),
        "catalog_category": str(record.get("catalog_category", "")),
        "control_role": str(record.get("control_role", "")),
        "disposition": disposition,
        "source_construct_hint": construct_hint,
        "source_vocabulary_needs": vocabulary_needs,
        "handoff_notes": notes,
        "runtime_evidence": {
            "telemetry_artifact_root": telemetry_root,
            "checkpoint_count": len(tuple(record.get("checkpoint_links", ()))),
            "observed_evidence_fields": [
                str(item) for item in record.get("observed_evidence_fields", ())
            ],
            "predicted_evidence_fields": [
                str(item) for item in record.get("predicted_evidence_fields", ())
            ],
            "event_counts_by_kind": dict(record.get("event_counts_by_kind", {})),
        },
        "future_source_work_must_preserve": _preservation_requirements(record),
        "source_claim_status": "runtime_evidence_only",
        "explicit_non_claims": list(
            dict.fromkeys(tuple(record.get("non_claims", ())) + _BASE_NON_CLAIMS)
        ),
    }


def _classify_record(record: Mapping[str, Any]) -> tuple[str, str, list[str], str]:
    phenomenon = str(record.get("phenomenon", ""))
    category = str(record.get("catalog_category", ""))
    status = str(record.get("review_status", ""))
    if status == "accepted" and category in _SOURCE_LIFECYCLE_CATEGORIES:
        return (
            "source_expression_candidate",
            _construct_hint(phenomenon),
            _source_vocabulary_for_phenomenon(phenomenon),
            "Accepted lifecycle evidence can seed later source-expression design.",
        )
    if phenomenon == "transport_basin_rerouting" and status == "accepted":
        return (
            "requires_new_source_vocabulary",
            "transport_route_or_basin_rerouting_constraint",
            [
                "source-level route preference",
                "basin redirection or saddle/ridge control",
                "telemetry-backed flux contrast predicate",
            ],
            "Transport rerouting is source-relevant but needs explicit vocabulary before lowering.",
        )
    if category in {"negative_control", "quiescent_control"}:
        return (
            "requires_new_source_vocabulary",
            _construct_hint(phenomenon),
            [
                "source-level control role",
                "absence-of-event expectation",
                "pass/fail perturbation declaration",
            ],
            "Control evidence is useful for source fixtures but is not an event motif.",
        )
    if phenomenon in _RUNTIME_ONLY_PHENOMENA or category == "diagnostic_comparator":
        return (
            "runtime_only",
            "runtime_diagnostic_or_backend_constraint",
            [],
            "This record is a runtime invariant, cache/backend diagnostic, or implementation comparator.",
        )
    return (
        "requires_new_source_vocabulary",
        _construct_hint(phenomenon),
        ["source construct boundary still undefined"],
        "No precise source vocabulary exists yet for this reviewed runtime record.",
    )


def _construct_hint(phenomenon: str) -> str:
    if "spark" in phenomenon:
        return "hybrid_spark_precursor"
    if "appendix_e" in phenomenon or "hierarchy" in phenomenon:
        return "cell_division_or_daughter_sink_split"
    if "choice" in phenomenon or "collapse" in phenomenon:
        return "choice_collapse_basin_constraint"
    if "growth" in phenomenon:
        return "growth_locus_with_outward_pressure"
    if "transport" in phenomenon:
        return "transport_route_or_basin_rerouting_constraint"
    if "quiescent" in phenomenon:
        return "quiescent_basin_constraint"
    return "runtime_motif"


def _source_vocabulary_for_phenomenon(phenomenon: str) -> list[str]:
    if "spark" in phenomenon:
        return [
            "saturated identity region",
            "row-basis Hessian or tensor gate",
            "column proxy fallback status",
        ]
    if "appendix_e" in phenomenon or "hierarchy" in phenomenon:
        return [
            "post-expansion daughter sink region",
            "hierarchy parent/child relation",
            "module basin support",
        ]
    if "choice" in phenomenon or "collapse" in phenomenon:
        return [
            "Morse-style competing basins",
            "collapse target selector",
            "choice compatibility predicate",
        ]
    if "growth" in phenomenon:
        return [
            "inactive boundary port",
            "outward flux pressure",
            "birth-rate parameter",
        ]
    return ["runtime-backed source construct vocabulary"]


def _preservation_requirements(record: Mapping[str, Any]) -> list[str]:
    phenomenon = str(record.get("phenomenon", ""))
    fields = [str(item) for item in record.get("observed_evidence_fields", ())]
    requirements = ["linked reviewed runtime motif id", "runtime evidence paths"]
    if "spark" in phenomenon:
        requirements.extend(
            ["saturation gate evidence", "hybrid spark event ordering"]
        )
    if "appendix_e" in phenomenon or "hierarchy" in phenomenon:
        requirements.extend(["daughter sink evidence", "hierarchy mutation evidence"])
    if "choice" in phenomenon or "collapse" in phenomenon:
        requirements.extend(["choice/collapse event evidence", "basin summary fields"])
    if "growth" in phenomenon:
        requirements.extend(["growth event evidence", "birth-pressure telemetry"])
    if "transport" in phenomenon:
        requirements.extend(["transport flux telemetry", "basin rerouting contrast"])
    if fields:
        requirements.append("observed evidence field list")
    return list(dict.fromkeys(requirements))


def _markdown_handoff(
    payload: Mapping[str, Any],
    session: GRC9V3SourceHandoffSession,
) -> str:
    summary = session.to_mapping()
    lines = [
        "# GRC9V3 Source-Language Handoff",
        "",
        f"Version: `{payload['version']}`",
        f"Session: `{session.session_id}`",
        f"Source catalog session: `{session.source_catalog_session_id}`",
        "",
        "## Boundary",
        "",
        str(payload["boundary_statement"]),
        "",
        "## Summary",
        "",
        f"- Runtime records reviewed: `{summary['motif_count']}`",
        f"- Source-expression candidates: `{summary['source_expression_candidate_count']}`",
        f"- Require new source vocabulary: `{summary['requires_new_source_vocabulary_count']}`",
        f"- Runtime-only records: `{summary['runtime_only_count']}`",
        "",
        "## Source-Expression Candidates",
        "",
    ]
    lines.extend(_markdown_entry(entry) for entry in payload["source_expression_candidates"])
    lines.extend(["", "## Require New Source Vocabulary", ""])
    lines.extend(_markdown_entry(entry) for entry in payload["requires_new_source_vocabulary"])
    lines.extend(["", "## Runtime Only", ""])
    lines.extend(_markdown_entry(entry) for entry in payload["runtime_only"])
    return "\n".join(lines) + "\n"


def _markdown_entry(entry: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"### {entry['motif_id']}",
            "",
            f"- Lane: `{entry['lane_name']}`",
            f"- Phenomenon: `{entry['phenomenon']}`",
            f"- Status: `{entry['review_status']}`",
            f"- Disposition: `{entry['disposition']}`",
            f"- Source construct hint: `{entry['source_construct_hint']}`",
            f"- Vocabulary needs: `{', '.join(entry['source_vocabulary_needs']) or 'n/a'}`",
            "",
            str(entry["handoff_notes"]),
            "",
        ]
    )


def _session_manifest(session: GRC9V3SourceHandoffSession) -> Mapping[str, Any]:
    summary = session.to_mapping()
    return {
        "session_id": session.session_id,
        "program": "grc9v3_phenomenology_discovery",
        "family": "grc9v3",
        "track": "phenomenology_discovery",
        "iteration": "I10_source_language_handoff",
        "session_kind": "source_language_handoff",
        "phenomenon": "GRC9V3 runtime motif source-language planning handoff",
        "seed_family": session.source_catalog_session_id,
        "control_role": "handoff",
        "status": "completed",
        "created_at": "2026-04-26",
        "git_revision": _git_revision(),
        "dirty_worktree": None,
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_source_handoff --session-id {session.session_id}"
        ),
        "input_paths": [session.source_catalog_path],
        "output_paths": [
            session.handoff_json_path,
            session.handoff_markdown_path,
            session.report_path,
        ],
        "observation_summary": (
            f"{summary['source_expression_candidate_count']} source-expression candidates, "
            f"{summary['requires_new_source_vocabulary_count']} vocabulary-needed records, "
            f"{summary['runtime_only_count']} runtime-only records."
        ),
        "non_claims": list(_BASE_NON_CLAIMS),
    }


def _write_summary_markdown(path: Path, session: GRC9V3SourceHandoffSession) -> None:
    summary = session.to_mapping()
    lines = [
        f"# {session.session_id} Source-Language Handoff Summary",
        "",
        f"- Runtime records: `{summary['motif_count']}`",
        f"- Source-expression candidates: `{summary['source_expression_candidate_count']}`",
        f"- Require new source vocabulary: `{summary['requires_new_source_vocabulary_count']}`",
        f"- Runtime only: `{summary['runtime_only_count']}`",
    ]
    _write_text(path, "\n".join(lines) + "\n")


def _write_readme(root: Path, session: GRC9V3SourceHandoffSession) -> None:
    lines = [
        f"# {session.session_id}. GRC9V3 Source-Language Handoff",
        "",
        "Status: `completed`",
        "",
        "Replay:",
        "",
        "```bash",
        (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_source_handoff --session-id {session.session_id}"
        ),
        "```",
        "",
        "Primary artifacts:",
        "",
        "- `source_language_handoff.json`",
        "- `source_language_handoff.md`",
        "- `reports/source_language_handoff_report.json`",
        "- `reports/source_language_handoff_summary.md`",
    ]
    _write_text(root / "README.md", "\n".join(lines) + "\n")


def _append_experimental_log(session: GRC9V3SourceHandoffSession) -> None:
    EXPERIMENTAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not EXPERIMENTAL_LOG_PATH.exists():
        EXPERIMENTAL_LOG_PATH.write_text(_experimental_log_header(), encoding="utf-8")
    text = EXPERIMENTAL_LOG_PATH.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if not line.startswith(f"| `{session.session_id}` |")]
    summary = session.to_mapping()
    lines.append(
        f"| `{session.session_id}` | `completed` | `source_language_handoff` | "
        "`I10_source_language_handoff` | GRC9V3 runtime motif source-language planning handoff | "
        f"`{session.source_catalog_session_id}` | "
        f"`outputs/grc9v3/phenomenology_discovery/sessions/{session.session_id}/` | "
        f"Iteration 10: {summary['source_expression_candidate_count']} source candidates, "
        f"{summary['requires_new_source_vocabulary_count']} vocabulary-needed, "
        f"{summary['runtime_only_count']} runtime-only |"
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


def _read_required_json(path: Path, description: str) -> Mapping[str, Any]:
    if not path.exists():
        raise FileNotFoundError(2, f"{description} missing", str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


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
    parser.add_argument("--session-id", default="S0014")
    parser.add_argument("--source-catalog-session-id", default="S0013")
    parser.add_argument("--session-root", default=None)
    parser.add_argument("--source-catalog-path", default=None)
    parser.add_argument("--full-json", action="store_true")
    args = parser.parse_args(argv)
    session = run_grc9v3_source_handoff(
        session_id=args.session_id,
        source_catalog_session_id=args.source_catalog_session_id,
        session_root=args.session_root,
        source_catalog_path=args.source_catalog_path,
    )
    payload = session.to_mapping()
    if args.full_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            {
                "session_id": session.session_id,
                "source_expression_candidate_count": payload[
                    "source_expression_candidate_count"
                ],
                "requires_new_source_vocabulary_count": payload[
                    "requires_new_source_vocabulary_count"
                ],
                "runtime_only_count": payload["runtime_only_count"],
                "handoff_json_path": session.handoff_json_path,
                "handoff_markdown_path": session.handoff_markdown_path,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "GRC9V3_SOURCE_HANDOFF_VERSION",
    "GRC9V3SourceHandoffSession",
    "run_grc9v3_source_handoff",
]
