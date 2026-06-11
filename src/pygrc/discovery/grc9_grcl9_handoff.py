"""GRCL-9 planning handoff for reviewed GRC9-native discovery motifs."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any

from .grc9_manifest import is_session_id


GRC9_GRCL9_HANDOFF_VERSION = "grc9_grcl9_handoff_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9/phenomenology_discovery/sessions")
_NO_TRANSLATION_CLAIM = (
    "This handoff does not implement GRCL-9 lowering and does not claim that "
    "any accepted GRC9 motif is already a source-language construct."
)
_BASE_NON_CLAIMS = (
    "no_grcl9_lowering_implemented",
    "no_source_language_construct_claim",
    "no_grcv3_semantics",
    "no_lorentzian_causal_layer",
    "no_observer_semantics",
)


@dataclass(frozen=True)
class GRC9GRCL9HandoffSession:
    session_id: str
    reviewed_session_id: str
    reviewed_catalog_path: str
    markdown_path: str
    json_path: str
    report_path: str
    motif_count: int
    accepted_count: int
    suitability_counts: Mapping[str, int]

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "reviewed_session_id": self.reviewed_session_id,
            "version": GRC9_GRCL9_HANDOFF_VERSION,
            "reviewed_catalog_path": self.reviewed_catalog_path,
            "markdown_path": self.markdown_path,
            "json_path": self.json_path,
            "report_path": self.report_path,
            "motif_count": self.motif_count,
            "accepted_count": self.accepted_count,
            "suitability_counts": dict(sorted(self.suitability_counts.items())),
        }


def run_grc9_grcl9_handoff(
    *,
    session_id: str = "S0026",
    reviewed_session_id: str = "S0025",
    session_root: str | Path | None = None,
    reviewed_catalog_path: str | Path | None = None,
) -> GRC9GRCL9HandoffSession:
    """Write a GRCL-9 planning handoff from accepted GRC9-native motifs."""

    if not is_session_id(session_id) or not is_session_id(reviewed_session_id):
        raise ValueError("session ids must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    source_path = (
        Path(reviewed_catalog_path)
        if reviewed_catalog_path is not None
        else DISCOVERY_SESSION_ROOT / reviewed_session_id / "reviewed_motif_catalog.json"
    )
    reviewed_catalog = _read_required_json(source_path, "reviewed motif catalog")
    accepted_motifs = tuple(
        motif
        for motif in reviewed_catalog.get("accepted_motifs", ())
        if isinstance(motif, Mapping)
    )
    entries = tuple(_handoff_entry(motif) for motif in accepted_motifs)
    payload = {
        "version": GRC9_GRCL9_HANDOFF_VERSION,
        "session_id": session_id,
        "reviewed_session_id": reviewed_session_id,
        "source_catalog_path": str(source_path),
        "boundary_statement": _NO_TRANSLATION_CLAIM,
        "accepted_count": len(entries),
        "entries": entries,
        "non_claims": sorted(
            {
                claim
                for entry in entries
                for claim in tuple(entry.get("explicit_non_claims", ()))
            }
            | set(_BASE_NON_CLAIMS)
        ),
    }
    markdown_path = root / "grcl9_suitability_catalog.md"
    json_path = root / "grcl9_suitability_catalog.json"
    report_path = reports_root / "grcl9_handoff_report.json"
    _write_text(markdown_path, _markdown_catalog(payload))
    _write_json(json_path, payload)
    suitability_counts = _suitability_counts(entries)
    session = GRC9GRCL9HandoffSession(
        session_id=session_id,
        reviewed_session_id=reviewed_session_id,
        reviewed_catalog_path=str(source_path),
        markdown_path=str(markdown_path),
        json_path=str(json_path),
        report_path=str(report_path),
        motif_count=len(entries),
        accepted_count=len(entries),
        suitability_counts=suitability_counts,
    )
    _write_json(report_path, session.to_mapping())
    _write_json(root / "session_manifest.json", _session_manifest(session))
    _write_readme(root, session)
    return session


def _handoff_entry(motif: Mapping[str, Any]) -> Mapping[str, Any]:
    notes = dict(motif.get("notes", {})) if isinstance(motif.get("notes", {}), Mapping) else {}
    seed_family = str(notes.get("seed_family", motif.get("seed_name", "")))
    artifact_root = str(notes.get("artifact_root", ""))
    parameter_summary = _parameter_summary(notes.get("seed_parameters_path"))
    structural = _structural_requirements(seed_family, str(motif.get("lane", "")))
    return {
        "motif_id": str(motif["motif_id"]),
        "phenomenon": str(motif.get("phenomenon", "")),
        "lane": str(motif.get("lane", "")),
        "profile": str(motif.get("profile", "")),
        "seed_family": seed_family,
        "seed_name": str(motif.get("seed_name", "")),
        "seed_parameters_path": str(notes.get("seed_parameters_path", "")),
        "runtime_parameter_overrides_path": str(
            notes.get("runtime_parameter_overrides_path", "")
        ),
        "parameter_summary": parameter_summary,
        "artifact_root": artifact_root,
        "telemetry_paths": _telemetry_paths(artifact_root),
        "checkpoint_index_path": str(notes.get("checkpoint_index_path", "")),
        "grc9_graph_preconditions": structural["graph_preconditions"],
        "future_lowering_must_preserve": structural["future_lowering_must_preserve"],
        "observed_validation_fields": tuple(
            str(item) for item in motif.get("observed_evidence_fields", ())
        ),
        "predicted_evidence_fields": tuple(
            str(item) for item in motif.get("predicted_evidence_fields", ())
        ),
        "review_status": str(motif.get("review_status", "")),
        "confidence_score": int(motif.get("confidence_score", 0)),
        "suitability": structural["suitability"],
        "handoff_notes": structural["handoff_notes"],
        "explicit_non_claims": tuple(
            sorted(set(tuple(motif.get("non_claims", ())) + _BASE_NON_CLAIMS))
        ),
    }


def _structural_requirements(seed_family: str, lane_name: str) -> Mapping[str, Any]:
    if "spark_to_expansion" in seed_family or "spark_to_expansion" in lane_name:
        return {
            "suitability": "translation_candidate_after_source_lowering_design",
            "graph_preconditions": (
                "saturated spark-capable parent in fixed 9-port chart",
                "expansion policy exposes target effective degree",
                "module size changes are controlled by D_eff parameterization",
                "boundary reassignment remains column-preserving",
            ),
            "future_lowering_must_preserve": (
                "port chart saturation state before spark",
                "D_eff to module-size relation",
                "internal module conductance policy",
                "coherence transfer ratios and boundary reassignment evidence",
            ),
            "handoff_notes": (
                "Good candidate for a future source construct that requests "
                "controlled refinement, but no source syntax is defined here."
            ),
        }
    if "growth_pressure" in seed_family or "growth_pressure" in lane_name:
        return {
            "suitability": "translation_candidate_after_source_lowering_design",
            "graph_preconditions": (
                "parent has at least one inactive external port",
                "outward flux pressure is localized at candidate boundary port",
                "birth probability is governed by lambda_birth",
            ),
            "future_lowering_must_preserve": (
                "inactive-port availability",
                "outward flux pressure gradient",
                "birth probability and birth rule telemetry",
                "new node attachment path",
            ),
            "handoff_notes": (
                "Good candidate for future source-level growth pressure intent; "
                "this handoff only records the native GRC9 graph condition."
            ),
        }
    if "post_expansion_fission" in seed_family or "fission" in lane_name:
        return {
            "suitability": "translation_candidate_after_source_lowering_design",
            "graph_preconditions": (
                "post-expansion module supports two stable sink basins",
                "bridge and pole conductance create separable attractor geometry",
                "persistence window and minimum basin mass thresholds are configured",
            ),
            "future_lowering_must_preserve": (
                "two-sink post-expansion basin geometry",
                "identity fission persistence window",
                "minimum basin mass threshold",
                "confirmed fission summary field",
            ),
            "handoff_notes": (
                "Good candidate for future source-level split intent, constrained "
                "to Appendix E style persistence evidence."
            ),
        }
    if "spark_instability" in seed_family or "spark_instability" in lane_name:
        return {
            "suitability": "translation_candidate_after_source_lowering_design",
            "graph_preconditions": (
                "saturated candidate node",
                "row-tensor instability gate passes before expansion",
                "spark threshold and tau instability distinguish pass/fail controls",
            ),
            "future_lowering_must_preserve": (
                "saturation gate",
                "instability gate evidence",
                "threshold parameterization",
                "spark-to-expansion event ordering",
            ),
            "handoff_notes": (
                "Potential future source-level instability trigger; no GRCL-9 "
                "trigger semantics are introduced in this track."
            ),
        }
    if "spark_column_proxy" in seed_family or "spark_column_proxy" in lane_name:
        return {
            "suitability": "translation_candidate_after_source_lowering_design",
            "graph_preconditions": (
                "saturated candidate node",
                "column proxy diagnostic gate separates pass/fail controls",
                "spark threshold epsilon is recorded in telemetry",
            ),
            "future_lowering_must_preserve": (
                "9-port saturation",
                "column diagnostic proxy evidence",
                "epsilon spark threshold",
                "spark-to-expansion event ordering when pass condition holds",
            ),
            "handoff_notes": (
                "Potential future source-level spark precursor; this remains a "
                "native GRC9 diagnostic motif."
            ),
        }
    return {
        "suitability": "requires_additional_review_before_translation_planning",
        "graph_preconditions": ("review accepted motif graph preconditions manually",),
        "future_lowering_must_preserve": ("accepted telemetry evidence fields",),
        "handoff_notes": "No family-specific handoff template was available.",
    }


def _parameter_summary(seed_parameters_path: Any) -> Mapping[str, Any]:
    path_text = str(seed_parameters_path or "")
    if not path_text:
        return {}
    path_part, _, fragment = path_text.partition("#")
    if fragment != "raw_params":
        return {"source": path_text}
    path = Path(path_part)
    if not path.exists():
        return {"source": path_text, "status": "missing"}
    try:
        run_summary = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"source": path_text, "status": "invalid_json"}
    raw_params = run_summary.get("raw_params", {})
    evolution = raw_params.get("evolution", {}) if isinstance(raw_params, Mapping) else {}
    modes = (
        raw_params.get("constitutive_semantic_modes", {})
        if isinstance(raw_params, Mapping)
        else {}
    )
    summary: dict[str, Any] = {"source": path_text}
    for key in (
        "D_eff_target",
        "eps_spark",
        "tau_instability",
        "lambda_birth",
        "identity_fission_persistence_delta",
        "identity_fission_min_basin_mass",
        "w_bond",
    ):
        if isinstance(evolution, Mapping) and key in evolution:
            summary[key] = evolution[key]
    for key in ("expansion_distribution_mode", "boundary_mode", "frame_mode"):
        if isinstance(modes, Mapping) and key in modes:
            summary[key] = modes[key]
    return summary


def _telemetry_paths(artifact_root: str) -> Mapping[str, str]:
    if not artifact_root:
        return {}
    root = Path(artifact_root) / "telemetry"
    return {
        "steps": str(root / "steps.jsonl"),
        "events": str(root / "events.jsonl"),
        "run_summary": str(root / "run_summary.json"),
        "graph_checkpoints": str(root / "graph_checkpoints"),
    }


def _markdown_catalog(payload: Mapping[str, Any]) -> str:
    lines = [
        "# GRC9 To GRCL-9 Suitability Catalog",
        "",
        f"Version: `{payload['version']}`",
        f"Session: `{payload['session_id']}`",
        f"Reviewed source session: `{payload['reviewed_session_id']}`",
        "",
        "## Boundary",
        "",
        _NO_TRANSLATION_CLAIM,
        "",
        "This catalog starts from reviewed GRC9-native motifs only. It is a planning handoff for a later GRCL-9 translation phase.",
        "",
        "## Summary",
        "",
        f"- Accepted motifs: `{payload['accepted_count']}`",
        f"- Non-claims: `{', '.join(payload['non_claims'])}`",
        "",
        "## Accepted Motifs",
        "",
    ]
    for entry in payload["entries"]:
        lines.extend(_markdown_entry(entry))
    return "\n".join(lines) + "\n"


def _markdown_entry(entry: Mapping[str, Any]) -> list[str]:
    lines = [
        f"### {entry['motif_id']}",
        "",
        f"- Phenomenon: `{entry['phenomenon']}`",
        f"- Lane: `{entry['lane']}`",
        f"- Seed family: `{entry['seed_family']}`",
        f"- Seed parameters: `{entry['seed_parameters_path']}`",
        f"- Suitability: `{entry['suitability']}`",
        "",
        "GRC9 graph preconditions:",
    ]
    lines.extend(f"- {item}" for item in entry["grc9_graph_preconditions"])
    lines.append("")
    lines.append("Future lowering would need to preserve:")
    lines.extend(f"- {item}" for item in entry["future_lowering_must_preserve"])
    lines.append("")
    lines.append("Observed validation fields:")
    lines.extend(f"- `{item}`" for item in entry["observed_validation_fields"])
    lines.append("")
    lines.append("Telemetry:")
    for key, value in entry["telemetry_paths"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("Explicit non-claims:")
    lines.extend(f"- `{item}`" for item in entry["explicit_non_claims"])
    lines.append("")
    lines.append(str(entry["handoff_notes"]))
    lines.append("")
    return lines


def _suitability_counts(entries: Sequence[Mapping[str, Any]]) -> Mapping[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        key = str(entry.get("suitability", "unknown"))
        counts[key] = counts.get(key, 0) + 1
    return counts


def _session_manifest(session: GRC9GRCL9HandoffSession) -> Mapping[str, Any]:
    return {
        "session_id": session.session_id,
        "program": "grc9_phenomenology_discovery",
        "family": "grc9",
        "track": "phenomenology_discovery",
        "iteration": "I09_grcl9_translation_handoff",
        "session_kind": "handoff",
        "phenomenon": "grcl9 suitability planning handoff",
        "seed_family": session.reviewed_session_id,
        "control_role": "handoff",
        "status": "completed",
        "created_at": "2026-04-25",
        "git_revision": _git_revision(),
        "dirty_worktree": None,
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9_grcl9_handoff --session-id {session.session_id} "
            f"--reviewed-session-id {session.reviewed_session_id}"
        ),
        "input_paths": [session.reviewed_catalog_path],
        "output_paths": [session.markdown_path, session.json_path, session.report_path],
        "observation_summary": (
            f"Prepared GRCL-9 planning handoff for {session.accepted_count} accepted GRC9-native motifs."
        ),
        "non_claims": list(_BASE_NON_CLAIMS),
    }


def _write_readme(root: Path, session: GRC9GRCL9HandoffSession) -> None:
    lines = [
        f"# {session.session_id}. GRC9 To GRCL-9 Suitability Handoff",
        "",
        "Status: `completed`",
        "",
        "Replay:",
        "",
        "```bash",
        (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9_grcl9_handoff --session-id {session.session_id} "
            f"--reviewed-session-id {session.reviewed_session_id}"
        ),
        "```",
        "",
        "Primary artifacts:",
        "",
        "- `grcl9_suitability_catalog.md`",
        "- `grcl9_suitability_catalog.json`",
        "- `reports/grcl9_handoff_report.json`",
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


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
    parser.add_argument("--session-id", default="S0026")
    parser.add_argument("--reviewed-session-id", default="S0025")
    parser.add_argument("--session-root", default=None)
    parser.add_argument("--reviewed-catalog-path", default=None)
    parser.add_argument("--full-json", action="store_true")
    args = parser.parse_args(argv)
    session = run_grc9_grcl9_handoff(
        session_id=args.session_id,
        reviewed_session_id=args.reviewed_session_id,
        session_root=args.session_root,
        reviewed_catalog_path=args.reviewed_catalog_path,
    )
    payload = session.to_mapping()
    if args.full_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            {
                "session_id": session.session_id,
                "reviewed_session_id": session.reviewed_session_id,
                "accepted_count": session.accepted_count,
                "markdown_path": session.markdown_path,
                "json_path": session.json_path,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "GRC9_GRCL9_HANDOFF_VERSION",
    "GRC9GRCL9HandoffSession",
    "run_grc9_grcl9_handoff",
]
