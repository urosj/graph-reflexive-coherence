"""Checkpoint and visual artifact index for GRC9 discovery motifs."""

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


GRC9_CHECKPOINT_VISUAL_INDEX_VERSION = "grc9_checkpoint_visual_index_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9/phenomenology_discovery/sessions")
_VISUAL_FILENAMES = (
    "visualization/graph_sequence.png",
    "visualization/graph_animation.gif",
    "visualization/graph_layouts.json",
    "visualization/graph_html/final_graph.html",
    "visualization/trajectories.png",
    "visualization/events.png",
    "visualization/report_panel.png",
)


@dataclass(frozen=True)
class GRC9CheckpointLink:
    checkpoint_id: str
    step_index: int
    path: str
    link_kind: str
    event_counts_by_kind_window: Mapping[str, int]

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "step_index": self.step_index,
            "path": self.path,
            "link_kind": self.link_kind,
            "event_counts_by_kind_window": dict(self.event_counts_by_kind_window),
        }


@dataclass(frozen=True)
class GRC9MotifCheckpointVisualRecord:
    motif_id: str
    session_id: str
    lane_name: str
    phenomenon: str
    confidence_label: str
    confidence_score: int
    step_window: tuple[int, int]
    event_steps: tuple[int, ...]
    checkpoint_links: tuple[GRC9CheckpointLink, ...]
    missing_exact_steps: tuple[int, ...]
    nearest_before_after: Mapping[int, Mapping[str, Any]]
    visual_artifacts: tuple[str, ...]
    visual_status: str
    artifact_root: str

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "motif_id": self.motif_id,
            "session_id": self.session_id,
            "lane_name": self.lane_name,
            "phenomenon": self.phenomenon,
            "confidence_label": self.confidence_label,
            "confidence_score": self.confidence_score,
            "step_window": list(self.step_window),
            "event_steps": list(self.event_steps),
            "checkpoint_links": [item.to_mapping() for item in self.checkpoint_links],
            "missing_exact_steps": list(self.missing_exact_steps),
            "nearest_before_after": {
                str(step_index): dict(value)
                for step_index, value in self.nearest_before_after.items()
            },
            "visual_artifacts": list(self.visual_artifacts),
            "visual_status": self.visual_status,
            "artifact_root": self.artifact_root,
        }


@dataclass(frozen=True)
class GRC9SkippedMotifRecord:
    motif_id: str
    lane_name: str
    reason: str
    missing_path: str | None = None

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "motif_id": self.motif_id,
            "lane_name": self.lane_name,
            "reason": self.reason,
            "missing_path": self.missing_path,
        }


@dataclass(frozen=True)
class GRC9CheckpointVisualIndexSession:
    session_id: str
    selector_session_id: str
    records: tuple[GRC9MotifCheckpointVisualRecord, ...]
    report_path: str
    visual_index_path: str
    skipped_motifs: tuple[GRC9SkippedMotifRecord, ...] = ()

    def to_mapping(self) -> Mapping[str, Any]:
        labels = Counter(record.confidence_label for record in self.records)
        visual_statuses = Counter(record.visual_status for record in self.records)
        nearest_summary = _nearest_distance_summary(self.records)
        return {
            "session_id": self.session_id,
            "selector_session_id": self.selector_session_id,
            "version": GRC9_CHECKPOINT_VISUAL_INDEX_VERSION,
            "record_count": len(self.records),
            "skipped_motif_count": len(self.skipped_motifs),
            "confidence_counts": dict(sorted(labels.items())),
            "visual_status_counts": dict(sorted(visual_statuses.items())),
            "records_with_missing_exact_count": sum(
                1 for record in self.records if record.missing_exact_steps
            ),
            "missing_exact_step_count": nearest_summary["missing_exact_step_count"],
            "nearest_distance_summary": nearest_summary,
            "records": [record.to_mapping() for record in self.records],
            "skipped_motifs": [item.to_mapping() for item in self.skipped_motifs],
            "report_path": self.report_path,
            "visual_index_path": self.visual_index_path,
        }


def run_grc9_checkpoint_visual_index(
    *,
    session_id: str = "S0023",
    selector_session_id: str = "S0022",
    session_root: str | Path | None = None,
    selector_manifest_path: str | Path | None = None,
) -> GRC9CheckpointVisualIndexSession:
    """Build checkpoint and visual index records for selector motif candidates."""

    if not is_session_id(session_id) or not is_session_id(selector_session_id):
        raise ValueError("session ids must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    manifest_path = (
        Path(selector_manifest_path)
        if selector_manifest_path is not None
        else DISCOVERY_SESSION_ROOT / selector_session_id / "selector_manifest.json"
    )
    manifest = _read_required_json(manifest_path, "selector manifest")
    records: list[GRC9MotifCheckpointVisualRecord] = []
    skipped_motifs: list[GRC9SkippedMotifRecord] = []
    for motif in manifest.get("motifs", ()):
        if not isinstance(motif, Mapping):
            continue
        try:
            records.append(_record_for_motif(motif))
        except (FileNotFoundError, ValueError) as exc:
            skipped_motifs.append(_skipped_motif_record(motif, exc))
    visual_index_path = root / "visual_index.json"
    report_path = reports_root / "checkpoint_visual_index_report.json"
    session = GRC9CheckpointVisualIndexSession(
        session_id=session_id,
        selector_session_id=selector_session_id,
        records=tuple(records),
        report_path=str(report_path),
        visual_index_path=str(visual_index_path),
        skipped_motifs=tuple(skipped_motifs),
    )
    _write_json(visual_index_path, _visual_index_payload(session))
    _write_json(report_path, session.to_mapping())
    _write_json(root / "session_manifest.json", _session_manifest(session))
    _write_readme(root, session)
    _write_summary_markdown(reports_root / "checkpoint_visual_index_summary.md", session)
    return session


def _record_for_motif(motif: Mapping[str, Any]) -> GRC9MotifCheckpointVisualRecord:
    notes = motif.get("notes", {})
    artifact_root = str(notes.get("artifact_root", "")) if isinstance(notes, Mapping) else ""
    if not artifact_root:
        raise ValueError(f"motif {motif.get('motif_id')} is missing notes.artifact_root")
    lane_name = str(motif["lane"])
    session_ids = tuple(str(item) for item in motif.get("session_ids", ()))
    session_id = session_ids[0] if session_ids else ""
    step_window_raw = motif.get("step_window", (0, 0))
    step_window = (int(step_window_raw[0]), int(step_window_raw[1]))
    telemetry_root = Path(artifact_root) / "telemetry"
    checkpoint_root = telemetry_root / "graph_checkpoints"
    checkpoint_index = _read_required_json(
        checkpoint_root / "index.json",
        f"checkpoint index for motif {motif.get('motif_id')}",
    )
    checkpoint_by_step = {
        int(item["step_index"]): item
        for item in checkpoint_index.get("checkpoints", ())
        if isinstance(item, Mapping) and item.get("step_index") is not None
    }
    event_steps = _event_steps(telemetry_root / "events.jsonl")
    requested_steps = _steps_to_link(step_window=step_window, event_steps=event_steps)
    links: list[GRC9CheckpointLink] = []
    missing_exact_steps: list[int] = []
    nearest: dict[int, Mapping[str, Any]] = {}
    for step_index in requested_steps:
        checkpoint = checkpoint_by_step.get(step_index)
        if checkpoint is not None:
            links.append(_checkpoint_link(checkpoint, checkpoint_root, "exact"))
            continue
        missing_exact_steps.append(step_index)
        nearest[step_index] = _nearest_before_after(
            checkpoint_by_step,
            step_index,
            checkpoint_root,
        )
    visual_artifacts = tuple(
        str(Path(artifact_root) / filename)
        for filename in _VISUAL_FILENAMES
        if (Path(artifact_root) / filename).exists()
    )
    return GRC9MotifCheckpointVisualRecord(
        motif_id=str(motif["motif_id"]),
        session_id=session_id,
        lane_name=lane_name,
        phenomenon=str(motif["phenomenon"]),
        confidence_label=str(motif["confidence_label"]),
        confidence_score=int(motif["confidence_score"]),
        step_window=step_window,
        event_steps=event_steps,
        checkpoint_links=tuple(_dedupe_links(links)),
        missing_exact_steps=tuple(missing_exact_steps),
        nearest_before_after=nearest,
        visual_artifacts=visual_artifacts,
        visual_status="present" if visual_artifacts else "not_rendered",
        artifact_root=artifact_root,
    )


def _event_steps(path: Path) -> tuple[int, ...]:
    steps: set[int] = set()
    for event in _read_jsonl(path):
        if "step_index" in event:
            steps.add(int(event["step_index"]))
    return tuple(sorted(steps))


def _steps_to_link(*, step_window: tuple[int, int], event_steps: Sequence[int]) -> tuple[int, ...]:
    start, end = step_window
    steps = {start, end, *event_steps}
    return tuple(sorted(step for step in steps if start <= step <= end))


def _checkpoint_link(
    checkpoint: Mapping[str, Any],
    checkpoint_root: Path,
    link_kind: str,
) -> GRC9CheckpointLink:
    relative_path = str(checkpoint.get("path", ""))
    return GRC9CheckpointLink(
        checkpoint_id=str(checkpoint["checkpoint_id"]),
        step_index=int(checkpoint["step_index"]),
        path=str(checkpoint_root / relative_path),
        link_kind=link_kind,
        event_counts_by_kind_window={
            str(key): int(value)
            for key, value in dict(checkpoint.get("event_counts_by_kind_window", {})).items()
        },
    )


def _nearest_before_after(
    checkpoint_by_step: Mapping[int, Mapping[str, Any]],
    step_index: int,
    checkpoint_root: Path,
) -> Mapping[str, Any]:
    before_steps = [step for step in checkpoint_by_step if step < step_index]
    after_steps = [step for step in checkpoint_by_step if step > step_index]
    result: dict[str, Any] = {}
    if before_steps:
        result["before"] = _checkpoint_link(
            checkpoint_by_step[max(before_steps)],
            checkpoint_root,
            "nearest_before",
        ).to_mapping()
    if after_steps:
        result["after"] = _checkpoint_link(
            checkpoint_by_step[min(after_steps)],
            checkpoint_root,
            "nearest_after",
        ).to_mapping()
    return result


def _dedupe_links(links: Sequence[GRC9CheckpointLink]) -> tuple[GRC9CheckpointLink, ...]:
    by_id: dict[str, GRC9CheckpointLink] = {}
    for link in links:
        by_id[link.checkpoint_id] = link
    return tuple(by_id[key] for key in sorted(by_id, key=lambda value: by_id[value].step_index))


def _skipped_motif_record(
    motif: Mapping[str, Any],
    exc: FileNotFoundError | ValueError,
) -> GRC9SkippedMotifRecord:
    missing_path = getattr(exc, "filename", None)
    return GRC9SkippedMotifRecord(
        motif_id=str(motif.get("motif_id", "")),
        lane_name=str(motif.get("lane", "")),
        reason=str(exc),
        missing_path=str(missing_path) if missing_path else None,
    )


def _nearest_distance_summary(
    records: Sequence[GRC9MotifCheckpointVisualRecord],
) -> Mapping[str, int | float]:
    distances: list[int] = []
    for record in records:
        for step_index, neighbors in record.nearest_before_after.items():
            before = neighbors.get("before")
            after = neighbors.get("after")
            if isinstance(before, Mapping):
                distances.append(abs(step_index - int(before["step_index"])))
            if isinstance(after, Mapping):
                distances.append(abs(int(after["step_index"]) - step_index))
    if not distances:
        return {
            "missing_exact_step_count": sum(len(record.missing_exact_steps) for record in records),
            "nearest_distance_max": 0,
            "nearest_distance_mean": 0.0,
        }
    return {
        "missing_exact_step_count": sum(len(record.missing_exact_steps) for record in records),
        "nearest_distance_max": max(distances),
        "nearest_distance_mean": sum(distances) / len(distances),
    }


def _visual_index_payload(session: GRC9CheckpointVisualIndexSession) -> Mapping[str, Any]:
    return {
        "version": GRC9_CHECKPOINT_VISUAL_INDEX_VERSION,
        "session_id": session.session_id,
        "selector_session_id": session.selector_session_id,
        "visual_boundary": "index_only_no_new_rendering",
        "records": [record.to_mapping() for record in session.records],
        "skipped_motifs": [item.to_mapping() for item in session.skipped_motifs],
    }


def _session_manifest(session: GRC9CheckpointVisualIndexSession) -> Mapping[str, Any]:
    return {
        "session_id": session.session_id,
        "program": "grc9_phenomenology_discovery",
        "family": "grc9",
        "track": "phenomenology_discovery",
        "iteration": "I07_checkpoint_evidence_and_visual_index",
        "session_kind": "checkpoint_visual_index",
        "phenomenon": "checkpoint evidence and visual index",
        "seed_family": session.selector_session_id,
        "control_role": "motif_checkpoint_linking",
        "status": "completed",
        "created_at": "2026-04-25",
        "git_revision": _git_revision(),
        "dirty_worktree": None,
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9_checkpoint_visual_index --session-id {session.session_id} "
            f"--selector-session-id {session.selector_session_id}"
        ),
        "input_paths": [
            f"outputs/grc9/phenomenology_discovery/sessions/{session.selector_session_id}/selector_manifest.json",
        ],
        "output_paths": [
            session.visual_index_path,
            session.report_path,
        ],
        "telemetry_paths": [],
        "checkpoint_paths": sorted(
            {
                str(Path(record.artifact_root) / "telemetry" / "graph_checkpoints")
                for record in session.records
            }
        ),
        "visualization_paths": sorted(
            {path for record in session.records for path in record.visual_artifacts}
        ),
        "prediction_summary": "Every motif candidate should link to exact saved checkpoints for its event/window steps when every-step checkpoints exist.",
        "observation_summary": (
            f"Indexed {len(session.records)} motif candidates with "
            f"{sum(len(record.checkpoint_links) for record in session.records)} checkpoint links; "
            f"skipped {len(session.skipped_motifs)} motifs."
        ),
        "replay_notes": "This session indexes saved artifacts only; it does not render new visualization files.",
    }


def _write_readme(root: Path, session: GRC9CheckpointVisualIndexSession) -> None:
    root.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {session.session_id}. GRC9 Checkpoint Evidence And Visual Index",
        "",
        "Status: `completed`",
        "",
        "This session links selector motif candidates to saved graph checkpoints and records currently available visual artifacts.",
        "",
        "Replay:",
        "",
        "```bash",
        (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9_checkpoint_visual_index --session-id {session.session_id} "
            f"--selector-session-id {session.selector_session_id}"
        ),
        "```",
        "",
        f"Selector session: `{session.selector_session_id}`",
        f"Indexed motifs: `{len(session.records)}`",
        f"Skipped motifs: `{len(session.skipped_motifs)}`",
        f"Checkpoint links: `{sum(len(record.checkpoint_links) for record in session.records)}`",
        "",
        "Primary reports:",
        "",
        "- `visual_index.json`",
        "- `reports/checkpoint_visual_index_report.json`",
        "- `reports/checkpoint_visual_index_summary.md`",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary_markdown(
    path: Path,
    session: GRC9CheckpointVisualIndexSession,
) -> None:
    labels = Counter(record.confidence_label for record in session.records)
    visual_statuses = Counter(record.visual_status for record in session.records)
    exact_records = sum(1 for record in session.records if not record.missing_exact_steps)
    nearest_summary = _nearest_distance_summary(session.records)
    lines = [
        f"# {session.session_id} Checkpoint Evidence And Visual Index Summary",
        "",
        "## Scope",
        "",
        f"- Selector session: `{session.selector_session_id}`",
        f"- Indexed motifs: `{len(session.records)}`",
        f"- Skipped motifs: `{len(session.skipped_motifs)}`",
        f"- Records with exact checkpoint coverage: `{exact_records}`",
        f"- Total missing exact checkpoint steps: `{nearest_summary['missing_exact_step_count']}`",
        f"- Nearest checkpoint distance max/mean: `{nearest_summary['nearest_distance_max']}` / `{nearest_summary['nearest_distance_mean']:.2f}`",
        f"- Total checkpoint links: `{sum(len(record.checkpoint_links) for record in session.records)}`",
        f"- Confidence counts: `{dict(sorted(labels.items()))}`",
        f"- Visual status counts: `{dict(sorted(visual_statuses.items()))}`",
        "",
        "## Records",
        "",
    ]
    for record in session.records:
        lines.append(
            f"- `{record.session_id}/{record.lane_name}`: "
            f"{len(record.checkpoint_links)} checkpoint links, "
            f"`{record.visual_status}` visuals"
        )
    if session.skipped_motifs:
        lines.extend(["", "## Skipped Motifs", ""])
        for item in session.skipped_motifs:
            lines.append(
                f"- `{item.motif_id or item.lane_name}`: {item.reason}"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_required_json(path: Path, description: str) -> Mapping[str, Any]:
    if not path.exists():
        raise FileNotFoundError(2, f"{description} missing", str(path))
    return _read_json(path)


def _read_jsonl(path: Path) -> tuple[Mapping[str, Any], ...]:
    if not path.exists():
        return ()
    return tuple(
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


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
    parser.add_argument("--session-id", default="S0023")
    parser.add_argument("--selector-session-id", default="S0022")
    parser.add_argument("--session-root", default=None)
    parser.add_argument("--selector-manifest-path", default=None)
    parser.add_argument("--full-json", action="store_true")
    args = parser.parse_args(argv)
    session = run_grc9_checkpoint_visual_index(
        session_id=args.session_id,
        selector_session_id=args.selector_session_id,
        session_root=args.session_root,
        selector_manifest_path=args.selector_manifest_path,
    )
    payload = session.to_mapping()
    if args.full_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            {
                "session_id": session.session_id,
                "selector_session_id": session.selector_session_id,
                "record_count": payload["record_count"],
                "skipped_motif_count": payload["skipped_motif_count"],
                "missing_exact_step_count": payload["missing_exact_step_count"],
                "report_path": session.report_path,
                "visual_index_path": session.visual_index_path,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "GRC9_CHECKPOINT_VISUAL_INDEX_VERSION",
    "GRC9CheckpointLink",
    "GRC9CheckpointVisualIndexSession",
    "GRC9MotifCheckpointVisualRecord",
    "GRC9SkippedMotifRecord",
    "run_grc9_checkpoint_visual_index",
]
