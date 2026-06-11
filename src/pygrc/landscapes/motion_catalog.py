"""Reviewed catalog builder for motion-inference sessions."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
import json
from pathlib import Path
from typing import Any

from pygrc.core import canonical_json_dumps, canonicalize_json_value


MOTION_REVIEWED_CATALOG_VERSION = "motion_reviewed_catalog_iter13_v1"
DEFAULT_MOTION_OUTPUT_ROOT = Path("outputs/motion")
DEFAULT_MOTION_CATALOG_SESSION_ID = "S0006"
DEFAULT_SOURCE_SESSION_IDS = ("S0001", "S0002", "S0003", "S0004", "S0005")


def run_motion_reviewed_catalog_session(
    *,
    output_root: str | Path = DEFAULT_MOTION_OUTPUT_ROOT,
    session_id: str = DEFAULT_MOTION_CATALOG_SESSION_ID,
    source_session_ids: Sequence[str] = DEFAULT_SOURCE_SESSION_IDS,
) -> Mapping[str, Any]:
    """Build the reviewed motion catalog from replayable motion sessions."""

    root = Path(output_root)
    session_root = root / "sessions" / session_id
    session_root.mkdir(parents=True, exist_ok=True)
    source_sessions = tuple(_load_source_session(root, source_id) for source_id in source_session_ids)
    entries = _catalog_entries(root, source_sessions)
    catalog = {
        "session_version": MOTION_REVIEWED_CATALOG_VERSION,
        "session_id": session_id,
        "session_root": str(session_root),
        "source_session_ids": list(source_session_ids),
        "source_sessions": [session["summary"] for session in source_sessions],
        "entry_count": len(entries),
        "entries": entries,
        "aggregate": _aggregate_entries(entries),
        "family_limitations": _family_limitations(),
        "usage_notes": _usage_notes(),
        "remaining_gaps": _remaining_gaps(),
        "source_runtime_boundary": (
            "catalog_reviews_existing_motion_artifacts_only_no_new_motion_records"
        ),
        "authority_order": [
            "runtime_dynamics",
            "telemetry_and_checkpoints",
            "motion_inference",
            "interpretation_and_promotion",
            "reviewed_catalog",
        ],
        "non_claims": [
            "no_new_runtime_motion_claim",
            "no_new_observer_record_claim",
            "no_visual_only_promotion",
            "source_seeds_are_preconditions_not_motion_outcomes",
        ],
    }
    manifest = {
        "session_version": MOTION_REVIEWED_CATALOG_VERSION,
        "session_id": session_id,
        "source_session_ids": list(source_session_ids),
        "catalog_path": str(session_root / "reviewed_motion_catalog.json"),
        "summary_path": str(session_root / "reviewed_motion_catalog.md"),
        "replay_command": (
            "PYTHONPATH=src python -m pygrc.landscapes.motion_catalog "
            f"--output-root {root} --session-id {session_id}"
        ),
    }
    _write_json(session_root / "session_manifest.json", manifest)
    _write_json(session_root / "reviewed_motion_catalog.json", catalog)
    _write_text(session_root / "reviewed_motion_catalog.md", _catalog_markdown(catalog))
    return canonicalize_json_value(catalog)


def _load_source_session(root: Path, session_id: str) -> Mapping[str, Any]:
    session_root = root / "sessions" / session_id
    run_report_path = session_root / "run_report.json"
    landscape_summary_path = session_root / "landscape_motion_summary.json"
    run_report = _read_json(run_report_path) if run_report_path.exists() else {}
    landscape_summary = _read_json(landscape_summary_path) if landscape_summary_path.exists() else {}
    interpretation = _optional_json(session_root / "interpretation" / "motion_interpretation_summary.json")
    dense = _optional_json(session_root / "interpretation" / "dense_window_calibration_summary.json")
    promotion = _optional_json(session_root / "interpretation" / "identity_fission_promotion_summary.json")
    visual_manifest = _optional_json(session_root / "visualizations" / "visual_manifest.json")
    animated_manifest = _optional_json(session_root / "visualizations" / "animated_visual_manifest.json")
    summary = {
        "session_id": session_id,
        "session_root": str(session_root),
        "session_version": str(
            run_report.get("session_version")
            or landscape_summary.get("session_version")
            or "unknown"
        ),
        "run_report_path": str(run_report_path) if run_report_path.exists() else "",
        "landscape_motion_summary_path": (
            str(landscape_summary_path) if landscape_summary_path.exists() else ""
        ),
        "interpretation_summary_path": (
            str(session_root / "interpretation" / "motion_interpretation_summary.json")
            if interpretation
            else ""
        ),
        "dense_calibration_summary_path": (
            str(session_root / "interpretation" / "dense_window_calibration_summary.json")
            if dense
            else ""
        ),
        "identity_fission_promotion_summary_path": (
            str(session_root / "interpretation" / "identity_fission_promotion_summary.json")
            if promotion
            else ""
        ),
        "visual_manifest_path": (
            str(session_root / "visualizations" / "visual_manifest.json")
            if visual_manifest
            else ""
        ),
        "animated_visual_manifest_path": (
            str(session_root / "visualizations" / "animated_visual_manifest.json")
            if animated_manifest
            else ""
        ),
    }
    return {
        "summary": summary,
        "run_report": run_report,
        "landscape_summary": landscape_summary,
        "interpretation": interpretation,
        "dense": dense,
        "promotion": promotion,
    }


def _catalog_entries(root: Path, source_sessions: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    entries: list[Mapping[str, Any]] = []
    for session in source_sessions:
        session_id = str(session["summary"]["session_id"])
        if session_id == "S0001":
            entries.extend(_controlled_example_entries(session))
        elif session_id == "S0002":
            entries.extend(_authored_seed_entries(session))
        elif session_id == "S0003":
            entries.extend(_long_window_entries(session))
        elif session_id == "S0004":
            entries.extend(_complex_landscape_entries(session))
        elif session_id == "S0005":
            entries.extend(_confirmed_fission_entries(session))
    return sorted(entries, key=lambda entry: (entry["status"], entry["entry_id"]))


def _controlled_example_entries(session: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    report = _mapping(session.get("run_report", {}))
    examples = _sequence(report.get("examples", ()))
    result: list[Mapping[str, Any]] = []
    for example in examples:
        key = str(example.get("example_name", "unknown"))
        relationships = _relationship_counts(example.get("observer_relationships", {}))
        status = "negative_control" if bool(example.get("negative_control", False)) else "accepted"
        if key == "no_motion_negative_control":
            status = "negative_control"
        result.append(
            _entry(
                entry_id=f"motion-catalog-s0001-{key}",
                source_session_id="S0001",
                source_kind="controlled_structural_fixture",
                key=key,
                runtime_family=str(example.get("runtime_family", "unknown")),
                status=status,
                accepted_motion_kinds=tuple(example.get("expected_record_kinds", ())),
                relationship_counts=relationships,
                evidence_summary=str(example.get("purpose", "")),
                catalog_decision=(
                    "accept_controlled_observer_example"
                    if status == "accepted"
                    else "accept_no_motion_negative_control"
                ),
                artifact_paths=_base_artifacts("S0001", key, visual=True),
                non_claims=(
                    "controlled_fixture_not_source_language_proof",
                    "visuals_are_supporting_evidence_only",
                ),
            )
        )
    return result


def _authored_seed_entries(session: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    runs = _sequence(_mapping(session.get("run_report", {})).get("runs", ()))
    result = []
    for run in runs:
        key = str(run.get("seed_name", run.get("key", "unknown")))
        relationships = _relationship_counts(run.get("observer_relationships", {}))
        status = "accepted"
        decision = "accept_authored_seed_projection"
        if key == "motion_composite_split_merge_collapse":
            status = "ambiguous"
            decision = "retain_composite_identity_topology_disagreement"
        result.append(
            _entry(
                entry_id=f"motion-catalog-s0002-{key}",
                source_session_id="S0002",
                source_kind="authored_seed_projection",
                key=key,
                runtime_family=str(run.get("runtime_family", "unknown")),
                status=status,
                accepted_motion_kinds=tuple(run.get("target_motion_modes", ())),
                relationship_counts=relationships,
                evidence_summary=str(run.get("source_status", "source_seed_projection")),
                catalog_decision=decision,
                artifact_paths=_seed_artifacts("S0002", key, run),
                non_claims=tuple(run.get("non_claims", ()))
                or ("source_preconditions_only",),
            )
        )
    return result


def _long_window_entries(session: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    runs = _sequence(_mapping(session.get("run_report", {})).get("runs", ()))
    result = []
    for run in runs:
        key = str(run.get("seed_name", run.get("key", "unknown")))
        relationships = _relationship_counts(run.get("observer_relationships", {}))
        status = "accepted"
        decision = "accept_long_window_composite_motion"
        if "failed_relay" in key:
            status = "rejected"
            decision = "reject_identity_walk_without_continuity"
        elif "no_motion_negative" in key:
            status = "negative_control"
            decision = "accept_long_window_no_motion_control"
        elif "split_merge_collapse" in key:
            status = "ambiguous"
            decision = "accept_topological_cascade_keep_identity_disagreement"
        result.append(
            _entry(
                entry_id=f"motion-catalog-s0003-{key}",
                source_session_id="S0003",
                source_kind="long_window_authored_seed_projection",
                key=key,
                runtime_family=str(run.get("runtime_family", "unknown")),
                status=status,
                accepted_motion_kinds=tuple(run.get("target_motion_modes", ())),
                relationship_counts=relationships,
                evidence_summary="20+ checkpoint composite motion session",
                catalog_decision=decision,
                artifact_paths=_seed_artifacts("S0003", key, run, animated=True),
                non_claims=tuple(run.get("non_claims", ()))
                or ("source_preconditions_only",),
            )
        )
    return result


def _complex_landscape_entries(session: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    interpretation_by_key = {
        str(run.get("key", "unknown")): run
        for run in _sequence(_mapping(session.get("interpretation", {})).get("runs", ()))
    }
    dense_by_key = {
        str(run.get("key", "unknown")): run
        for run in _sequence(_mapping(session.get("dense", {})).get("runs", ()))
    }
    promotion_by_key = {
        str(run.get("key", "unknown")): run
        for run in _sequence(_mapping(session.get("promotion", {})).get("runs", ()))
    }
    result = []
    for key, run in sorted(interpretation_by_key.items()):
        relationships = _relationship_counts(run.get("motion_relationship_counts", {}))
        promotion = promotion_by_key.get(key, {})
        dense = dense_by_key.get(key, {})
        status = "diagnostic"
        decision = str(
            promotion.get("catalog_guidance")
            or dense.get("catalog_guidance")
            or run.get("catalog_recommendation")
            or "diagnostic_review"
        )
        if decision == "accept_topological_collapse_with_identity_calibration":
            status = "accepted_with_caveat"
        result.append(
            _entry(
                entry_id=f"motion-catalog-s0004-{key}",
                source_session_id="S0004",
                source_kind="complex_landscape_inference_bridge",
                key=key,
                runtime_family=str(run.get("runtime_family", "unknown")),
                status=status,
                accepted_motion_kinds=_accepted_kinds_from_relationships(relationships),
                relationship_counts=relationships,
                evidence_summary=(
                    "Complex landscape-inference bridge; identity-fission promotion "
                    f"count {int(promotion.get('promoted_identity_fission_count', 0) or 0)}."
                ),
                catalog_decision=decision,
                artifact_paths=_complex_artifacts(key, run),
                non_claims=(
                    "landscape_inference_and_motion_inference_are_separate_layers",
                    "identity_fission_not_promoted_for_s0004",
                ),
                review_notes=tuple(run.get("calibration_notes", ())),
            )
        )
    return result


def _confirmed_fission_entries(session: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    landscape_runs = {
        str(run.get("key", "unknown")): run
        for run in _sequence(_mapping(session.get("landscape_summary", {})).get("runs", ()))
    }
    result = []
    for run in _sequence(_mapping(session.get("promotion", {})).get("runs", ())):
        key = str(run.get("key", "unknown"))
        landscape_run = landscape_runs.get(key, {})
        promoted = int(run.get("promoted_identity_fission_count", 0) or 0)
        status = "accepted" if promoted > 0 else "diagnostic"
        result.append(
            _entry(
                entry_id=f"motion-catalog-s0005-{key}",
                source_session_id="S0005",
                source_kind="dense_confirmed_fission_seed_projection",
                key=key,
                runtime_family=str(run.get("runtime_family", "unknown")),
                status=status,
                accepted_motion_kinds=("identity", "topological"),
                relationship_counts=_relationship_counts(
                    landscape_run.get("motion_relationship_counts", {})
                ),
                evidence_summary=(
                    f"{promoted} compact provenance-linked identity-fission "
                    "candidates promoted by the 12.4 gate."
                ),
                catalog_decision=str(run.get("catalog_guidance", "")),
                artifact_paths=[
                    "outputs/motion/sessions/S0005/landscape_motion_summary.json",
                    "outputs/motion/sessions/S0005/interpretation/identity_fission_promotion_summary.json",
                    "outputs/motion/sessions/S0005/runs/motion_dense_confirmed_fission/motion_reports/identity_summary.json",
                    "configs/landscapes/seed/motion/motion_dense_confirmed_fission.seed.yaml",
                ],
                non_claims=(
                    "promotion_reads_existing_reports_only",
                    "broad_fanout_not_accepted_by_this_entry",
                ),
                review_notes=(
                    "S0005 is the positive dense identity-fission catalog example.",
                    "S0004 remains the negative/diagnostic dense-branching contrast.",
                ),
            )
        )
    return result


def _entry(
    *,
    entry_id: str,
    source_session_id: str,
    source_kind: str,
    key: str,
    runtime_family: str,
    status: str,
    accepted_motion_kinds: Sequence[str],
    relationship_counts: Mapping[str, Mapping[str, int]],
    evidence_summary: str,
    catalog_decision: str,
    artifact_paths: Sequence[str],
    non_claims: Sequence[str],
    review_notes: Sequence[str] = (),
) -> Mapping[str, Any]:
    return canonicalize_json_value(
        {
            "entry_id": entry_id,
            "source_session_id": source_session_id,
            "source_kind": source_kind,
            "key": key,
            "runtime_family": runtime_family,
            "status": status,
            "accepted_motion_kinds": list(dict.fromkeys(accepted_motion_kinds)),
            "relationship_counts": {
                observer: dict(counts)
                for observer, counts in sorted(relationship_counts.items())
            },
            "evidence_summary": evidence_summary,
            "catalog_decision": catalog_decision,
            "artifact_paths": list(dict.fromkeys(path for path in artifact_paths if path)),
            "non_claims": list(dict.fromkeys(non_claims)),
            "review_notes": list(review_notes),
        }
    )


def _base_artifacts(session_id: str, key: str, *, visual: bool = False) -> list[str]:
    paths = [
        f"outputs/motion/sessions/{session_id}/run_report.json",
        f"outputs/motion/sessions/{session_id}/runs/{key}/example_manifest.json",
    ]
    if visual:
        paths.extend(
            [
                f"outputs/motion/sessions/{session_id}/visualizations/{key}/motion_visual_summary.json",
                f"outputs/motion/sessions/{session_id}/visualizations/{key}/motion_graph.png",
                f"outputs/motion/sessions/{session_id}/visualizations/{key}/motion_timeline.png",
            ]
        )
    return paths


def _seed_artifacts(
    session_id: str,
    key: str,
    run: Mapping[str, Any],
    *,
    animated: bool = False,
) -> list[str]:
    projected_names = tuple(str(name) for name in run.get("projected_example_names", ()) if name)
    visual_key = projected_names[0] if projected_names else key
    paths = [
        f"outputs/motion/sessions/{session_id}/run_report.json",
        str(run.get("library_seed_path", "")),
        str(run.get("seed_path", "")),
    ]
    visual_root = f"outputs/motion/sessions/{session_id}/visualizations/{visual_key}"
    paths.extend(
        [
            f"{visual_root}/motion_visual_summary.json",
            f"{visual_root}/motion_graph.png",
            f"{visual_root}/motion_timeline.png",
        ]
    )
    if animated:
        paths.extend(
            [
                f"{visual_root}/motion_animated_summary.json",
                f"{visual_root}/motion_animation.gif",
                f"{visual_root}/motion_sequence.png",
            ]
        )
    return paths


def _complex_artifacts(key: str, run: Mapping[str, Any]) -> list[str]:
    report_dir = str(run.get("motion_report_dir", ""))
    return [
        "outputs/motion/sessions/S0004/landscape_motion_summary.json",
        "outputs/motion/sessions/S0004/interpretation/motion_interpretation_summary.json",
        "outputs/motion/sessions/S0004/interpretation/dense_window_calibration_summary.json",
        "outputs/motion/sessions/S0004/interpretation/identity_fission_promotion_summary.json",
        f"{report_dir}/identity_summary.json" if report_dir else "",
        f"outputs/motion/sessions/S0004/visualizations/{key}/motion_visual_summary.json",
    ]


def _accepted_kinds_from_relationships(
    relationships: Mapping[str, Mapping[str, int]],
) -> tuple[str, ...]:
    return tuple(
        observer
        for observer, counts in sorted(relationships.items())
        if sum(int(value) for value in counts.values()) > 0
    )


def _aggregate_entries(entries: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    status_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    kind_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    decision_counts: Counter[str] = Counter()
    for entry in entries:
        status_counts.update((str(entry.get("status", "unknown")),))
        family_counts.update((str(entry.get("runtime_family", "unknown")),))
        source_counts.update((str(entry.get("source_session_id", "unknown")),))
        decision_counts.update((str(entry.get("catalog_decision", "unknown")),))
        kind_counts.update(str(kind) for kind in entry.get("accepted_motion_kinds", ()))
    return canonicalize_json_value(
        {
            "status_counts": dict(sorted(status_counts.items())),
            "runtime_family_counts": dict(sorted(family_counts.items())),
            "accepted_motion_kind_counts": dict(sorted(kind_counts.items())),
            "source_session_counts": dict(sorted(source_counts.items())),
            "catalog_decision_counts": dict(sorted(decision_counts.items())),
            "accepted_entry_ids": [
                str(entry["entry_id"])
                for entry in entries
                if str(entry.get("status")) in {"accepted", "accepted_with_caveat"}
            ],
            "diagnostic_entry_ids": [
                str(entry["entry_id"])
                for entry in entries
                if str(entry.get("status")) == "diagnostic"
            ],
            "ambiguous_entry_ids": [
                str(entry["entry_id"])
                for entry in entries
                if str(entry.get("status")) == "ambiguous"
            ],
            "rejected_entry_ids": [
                str(entry["entry_id"])
                for entry in entries
                if str(entry.get("status")) == "rejected"
            ],
        }
    )


def _family_limitations() -> Sequence[Mapping[str, Any]]:
    return canonicalize_json_value(
        [
            {
                "runtime_family": "grcv3",
                "limitations": [
                    "full coherence and representative motion evidence is available",
                    "port/frontier boundary evidence is family-limited",
                    "identity fission needs careful review when dense split records are produced",
                ],
            },
            {
                "runtime_family": "grc9",
                "limitations": [
                    "port/frontier motion is available",
                    "semantic basin and signed-Hessian evidence is weaker than GRC9V3",
                ],
            },
            {
                "runtime_family": "grc9v3",
                "limitations": [
                    "preferred family for combined identity, boundary, topology, and dense fission evidence",
                    "broad dense branching remains diagnostic unless the promotion gate accepts it",
                ],
            },
        ]
    )


def _usage_notes() -> Sequence[str]:
    return (
        "Use motion records as observed runtime-to-runtime relationships, not source-authored outcomes.",
        "Use LandscapeSeed motion seeds as preconditions only; observer reports decide whether motion happened.",
        "Use S0004 as the dense-branching diagnostic contrast and S0005 as the compact confirmed-fission positive control.",
        "Use visual artifacts for review and communication only; no visual-only promotion is allowed.",
        "Knowledge-graph exports should preserve the distinction between coherence, representative, identity, boundary, and topological motion.",
    )


def _remaining_gaps() -> Sequence[str]:
    return (
        "Live LandscapeSeed-to-runtime execution for motion seeds remains future work; current seed examples are structural projections.",
        "Temporal graph animations exist for long-window sessions, but dense visual sampling is still a review surface rather than evidence promotion.",
        "Local-observer ignorance and partial-graph motion inference are not implemented.",
        "Lorentzian/proper-time and scale-indexed FRC motion remain out of scope for the initial catalog.",
    )


def _catalog_markdown(catalog: Mapping[str, Any]) -> str:
    aggregate = _mapping(catalog.get("aggregate", {}))
    lines = [
        "# Reviewed Motion Catalog",
        "",
        f"- session: `{catalog['session_id']}`",
        f"- version: `{catalog['session_version']}`",
        f"- entries: `{catalog['entry_count']}`",
        f"- source sessions: `{catalog['source_session_ids']}`",
        "- authority: reviews existing motion artifacts only",
        "",
        "## Aggregate",
        "",
        f"- status counts: `{aggregate.get('status_counts', {})}`",
        f"- runtime families: `{aggregate.get('runtime_family_counts', {})}`",
        f"- accepted motion kinds: `{aggregate.get('accepted_motion_kind_counts', {})}`",
        f"- catalog decisions: `{aggregate.get('catalog_decision_counts', {})}`",
        "",
        "## Accepted And Accepted With Caveat",
        "",
    ]
    for entry in catalog.get("entries", ()):
        if entry.get("status") not in {"accepted", "accepted_with_caveat"}:
            continue
        lines.extend(_entry_lines(entry))
    lines.extend(["## Diagnostic", ""])
    for entry in catalog.get("entries", ()):
        if entry.get("status") != "diagnostic":
            continue
        lines.extend(_entry_lines(entry))
    lines.extend(["## Ambiguous, Rejected, And Negative Controls", ""])
    for entry in catalog.get("entries", ()):
        if entry.get("status") not in {"ambiguous", "rejected", "negative_control"}:
            continue
        lines.extend(_entry_lines(entry))
    lines.extend(["## Family Limitations", ""])
    for item in catalog.get("family_limitations", ()):
        lines.append(f"### {item['runtime_family']}")
        lines.append("")
        lines.extend(f"- {note}" for note in item.get("limitations", ()))
        lines.append("")
    lines.extend(["## Usage Notes", ""])
    lines.extend(f"- {note}" for note in catalog.get("usage_notes", ()))
    lines.extend(["", "## Remaining Gaps", ""])
    lines.extend(f"- {gap}" for gap in catalog.get("remaining_gaps", ()))
    lines.append("")
    return "\n".join(lines)


def _entry_lines(entry: Mapping[str, Any]) -> list[str]:
    lines = [
        f"### {entry['entry_id']}",
        "",
        f"- key: `{entry['key']}`",
        f"- status: `{entry['status']}`",
        f"- source session: `{entry['source_session_id']}`",
        f"- source kind: `{entry['source_kind']}`",
        f"- runtime family: `{entry['runtime_family']}`",
        f"- accepted motion kinds: `{entry['accepted_motion_kinds']}`",
        f"- catalog decision: `{entry['catalog_decision']}`",
        f"- relationship counts: `{entry['relationship_counts']}`",
        f"- evidence: {entry['evidence_summary']}",
    ]
    if entry.get("review_notes"):
        lines.append("- review notes:")
        lines.extend(f"  - {note}" for note in entry.get("review_notes", ()))
    if entry.get("artifact_paths"):
        lines.append("- artifacts:")
        lines.extend(f"  - `{path}`" for path in entry.get("artifact_paths", ())[:8])
    lines.append("")
    return lines


def _relationship_counts(raw: Any) -> Mapping[str, Mapping[str, int]]:
    if not isinstance(raw, Mapping):
        return {}
    result: dict[str, dict[str, int]] = {}
    for observer, values in raw.items():
        if isinstance(values, Mapping):
            result[str(observer)] = {
                str(key): int(value)
                for key, value in sorted(values.items())
                if isinstance(value, int | float)
            }
        elif isinstance(values, Sequence) and not isinstance(values, str | bytes):
            counts = Counter(str(value) for value in values)
            result[str(observer)] = dict(sorted(counts.items()))
    return result


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _read_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, Mapping) else {}


def _optional_json(path: Path) -> Mapping[str, Any]:
    return _read_json(path) if path.exists() else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json_dumps(payload) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the reviewed motion catalog.")
    parser.add_argument("--output-root", default=str(DEFAULT_MOTION_OUTPUT_ROOT))
    parser.add_argument("--session-id", default=DEFAULT_MOTION_CATALOG_SESSION_ID)
    parser.add_argument(
        "--source-session-id",
        action="append",
        dest="source_session_ids",
        help="Source motion session id. Can be repeated; defaults to S0001-S0005.",
    )
    args = parser.parse_args(argv)
    catalog = run_motion_reviewed_catalog_session(
        output_root=args.output_root,
        session_id=args.session_id,
        source_session_ids=tuple(args.source_session_ids or DEFAULT_SOURCE_SESSION_IDS),
    )
    print(canonical_json_dumps({"session_root": catalog["session_root"], "entry_count": catalog["entry_count"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_MOTION_CATALOG_SESSION_ID",
    "DEFAULT_SOURCE_SESSION_IDS",
    "MOTION_REVIEWED_CATALOG_VERSION",
    "run_motion_reviewed_catalog_session",
]
