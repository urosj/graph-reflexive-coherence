"""Motion review bridge for complex landscape-inference sessions."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from pygrc.core import canonical_json_dumps, canonicalize_json_value

from .motion_boundary import infer_boundary_motion
from .motion_coherence import infer_coherence_motion
from .motion_identity import infer_identity_motion
from .motion_representative import infer_representative_motion
from .motion_topological import infer_topological_motion


MOTION_LANDSCAPE_BRIDGE_SESSION_VERSION = "motion_landscape_bridge_iter12_1_v1"
DEFAULT_LANDSCAPE_INFERENCE_SESSION_MANIFEST = Path(
    "outputs/landscape_inference/sessions/S0013/session_manifest.json"
)
DEFAULT_MOTION_LANDSCAPE_OUTPUT_ROOT = Path("outputs/motion")
DEFAULT_MOTION_LANDSCAPE_SESSION_ID = "S0004"

_OBSERVER_FNS = {
    "coherence": infer_coherence_motion,
    "representative": infer_representative_motion,
    "identity": infer_identity_motion,
    "boundary": infer_boundary_motion,
    "topological": infer_topological_motion,
}


@dataclass(frozen=True)
class MotionLandscapeRun:
    """Motion observer result for one landscape-inference selected seed."""

    key: str
    runtime_family: str
    source_seed_name: str
    source_seed_path: str
    landscape_artifact_root: Path
    run_dir: Path
    motion_report_dir: Path
    observer_record_counts: Mapping[str, int]
    observer_relationships: Mapping[str, tuple[str, ...]]
    observer_motion_ids: Mapping[str, tuple[str, ...]]
    primitive_counts_by_type: Mapping[str, int]
    landscape_relationship_counts: Mapping[str, int]
    checkpoint_count_loaded: int
    visual_notes: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "example_name": self.key,
                "runtime_family": self.runtime_family,
                "source_seed_name": self.source_seed_name,
                "source_seed_path": self.source_seed_path,
                "landscape_artifact_root": str(self.landscape_artifact_root),
                "run_dir": str(self.run_dir),
                "motion_report_dir": str(self.motion_report_dir),
                "observer_record_counts": dict(self.observer_record_counts),
                "observer_relationships": {
                    key: list(value) for key, value in self.observer_relationships.items()
                },
                "observer_motion_ids": {
                    key: list(value) for key, value in self.observer_motion_ids.items()
                },
                "primitive_counts_by_type": dict(self.primitive_counts_by_type),
                "landscape_relationship_counts": dict(self.landscape_relationship_counts),
                "checkpoint_count_loaded": self.checkpoint_count_loaded,
                "visual_notes": list(self.visual_notes),
                "source_runtime_boundary": (
                    "landscape_inference_observes_runtime_motion_bridge_reuses_same_checkpoints"
                ),
            }
        )


@dataclass(frozen=True)
class MotionLandscapeBridgeSession:
    """Iteration 12.1 motion-over-landscape-inference bridge session."""

    session_id: str
    session_root: Path
    landscape_manifest_path: Path
    runs: tuple[MotionLandscapeRun, ...]
    visual_root: Path | None = None

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "session_version": MOTION_LANDSCAPE_BRIDGE_SESSION_VERSION,
                "session_id": self.session_id,
                "session_root": str(self.session_root),
                "landscape_manifest_path": str(self.landscape_manifest_path),
                "selected_landscape_example_count": len(self.runs),
                "visual_root": None if self.visual_root is None else str(self.visual_root),
                "runs": [run.to_mapping() for run in self.runs],
                "authority_order": [
                    "runtime_dynamics",
                    "telemetry_and_checkpoints",
                    "landscape_inference",
                    "motion_inference",
                    "static_and_animated_visualization",
                ],
            }
        )


def run_motion_landscape_bridge_session(
    *,
    landscape_manifest_path: str | Path = DEFAULT_LANDSCAPE_INFERENCE_SESSION_MANIFEST,
    output_root: str | Path = DEFAULT_MOTION_LANDSCAPE_OUTPUT_ROOT,
    session_id: str = DEFAULT_MOTION_LANDSCAPE_SESSION_ID,
    keys: Sequence[str] | None = None,
    observers: Sequence[str] = tuple(_OBSERVER_FNS),
    render_visuals: bool = True,
    animated: bool = True,
) -> MotionLandscapeBridgeSession:
    """Run motion observers over selected landscape-inference runtime artifacts."""

    manifest_path = Path(landscape_manifest_path)
    manifest = _read_json(manifest_path)
    selected = _selected_seed_entries(manifest, keys=keys)
    observer_names = _validate_observers(observers)
    session_root = Path(output_root) / "sessions" / session_id
    session_root.mkdir(parents=True, exist_ok=True)

    runs = tuple(
        _run_motion_for_landscape_entry(entry, observer_names=observer_names)
        for entry in selected
    )
    session = MotionLandscapeBridgeSession(
        session_id=session_id,
        session_root=session_root,
        landscape_manifest_path=manifest_path,
        runs=runs,
    )
    _write_json(session_root / "session_manifest.json", _session_manifest(session, manifest))
    _write_json(session_root / "run_report.json", session.to_mapping())
    _write_json(session_root / "landscape_motion_summary.json", _summary_report(session))
    _write_text(session_root / "landscape_motion_summary.md", _summary_markdown(session))
    _write_text(session_root / "README.md", _readme(session))
    _write_text(
        session_root / "rerun.sh",
        _rerun_script(
            output_root=Path(output_root),
            session_id=session_id,
            manifest_path=manifest_path,
            keys=keys,
            observers=observer_names,
            render_visuals=render_visuals,
            animated=animated,
        ),
    )
    if render_visuals:
        if animated:
            from pygrc.visualization.motion import render_motion_animated_visual_session

            visual_session = render_motion_animated_visual_session(session_root=session_root)
            visual_root = visual_session.visual_root
        else:
            from pygrc.visualization.motion import render_motion_visual_session

            visual_session = render_motion_visual_session(session_root=session_root)
            visual_root = visual_session.visual_root
        session = MotionLandscapeBridgeSession(
            session_id=session_id,
            session_root=session_root,
            landscape_manifest_path=manifest_path,
            runs=runs,
            visual_root=visual_root,
        )
        _write_json(session_root / "run_report.json", session.to_mapping())
        _write_json(session_root / "landscape_motion_summary.json", _summary_report(session))
        _write_text(session_root / "landscape_motion_summary.md", _summary_markdown(session))
    return session


def _run_motion_for_landscape_entry(
    entry: Mapping[str, Any],
    *,
    observer_names: Sequence[str],
) -> MotionLandscapeRun:
    key = str(entry["key"])
    artifact_root = Path(str(entry["artifact_root"]))
    report_dir = artifact_root / "motion_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    relationships: dict[str, tuple[str, ...]] = {}
    motion_ids: dict[str, tuple[str, ...]] = {}
    notes: list[str] = []
    for observer_name in observer_names:
        result = _OBSERVER_FNS[observer_name](artifact_root)
        report = result.to_report(
            source_session_id=key,
            source_artifact_paths=(str(artifact_root),),
        )
        _write_json(report_dir / f"{observer_name}_report.json", report.to_mapping())
        _write_json(report_dir / f"{observer_name}_summary.json", result.to_summary_mapping())
        records = tuple(result.records)
        counts[observer_name] = len(records)
        relationships[observer_name] = tuple(record.relationship for record in records)
        motion_ids[observer_name] = tuple(record.motion_id for record in records)
        if len(records) > 500:
            notes.append(
                f"{observer_name} emitted {len(records)} records; dense visual timelines are sampled"
            )
    return MotionLandscapeRun(
        key=key,
        runtime_family=str(entry.get("runtime_family", "unknown")),
        source_seed_name=str(entry.get("source_seed_name", "")),
        source_seed_path=str(entry.get("source_seed_path", "")),
        landscape_artifact_root=artifact_root,
        run_dir=artifact_root,
        motion_report_dir=report_dir,
        observer_record_counts=dict(sorted(counts.items())),
        observer_relationships=dict(sorted(relationships.items())),
        observer_motion_ids=dict(sorted(motion_ids.items())),
        primitive_counts_by_type={
            str(k): int(v) for k, v in dict(entry.get("primitive_counts_by_type", {})).items()
        },
        landscape_relationship_counts={
            str(k): int(v) for k, v in dict(entry.get("relationship_counts", {})).items()
        },
        checkpoint_count_loaded=int(entry.get("checkpoint_count_loaded", 0)),
        visual_notes=tuple(sorted(set(notes))),
    )


def _selected_seed_entries(
    manifest: Mapping[str, Any],
    *,
    keys: Sequence[str] | None,
) -> tuple[Mapping[str, Any], ...]:
    raw_entries = manifest.get("selected_seeds", ())
    if not isinstance(raw_entries, Sequence) or isinstance(raw_entries, str | bytes):
        raise ValueError("landscape manifest must contain selected_seeds sequence")
    entries = tuple(entry for entry in raw_entries if isinstance(entry, Mapping))
    if keys is None:
        return entries
    wanted = set(keys)
    selected = tuple(entry for entry in entries if str(entry.get("key")) in wanted)
    missing = wanted - {str(entry.get("key")) for entry in selected}
    if missing:
        raise ValueError(f"unknown selected landscape key(s): {sorted(missing)}")
    return selected


def _validate_observers(observers: Sequence[str]) -> tuple[str, ...]:
    names = tuple(str(observer) for observer in observers)
    unknown = sorted(set(names) - set(_OBSERVER_FNS))
    if unknown:
        raise ValueError(f"unknown motion observer(s): {unknown}")
    return names


def _session_manifest(
    session: MotionLandscapeBridgeSession,
    landscape_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "session_version": MOTION_LANDSCAPE_BRIDGE_SESSION_VERSION,
            "session_id": session.session_id,
            "source_landscape_session_id": landscape_manifest.get("session_id"),
            "source_landscape_iteration": landscape_manifest.get("iteration"),
            "landscape_manifest_path": str(session.landscape_manifest_path),
            "selected_landscape_example_count": len(session.runs),
            "motion_observers": sorted(_OBSERVER_FNS),
            "authority_order": session.to_mapping()["authority_order"],
            "replay_command": (
                "PYTHONPATH=src python -m pygrc.landscapes.motion_landscape_bridge "
                f"--landscape-manifest {session.landscape_manifest_path} "
                f"--output-root {session.session_root.parent.parent} "
                f"--session-id {session.session_id}"
            ),
        }
    )


def _summary_report(session: MotionLandscapeBridgeSession) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "session_version": MOTION_LANDSCAPE_BRIDGE_SESSION_VERSION,
            "session_id": session.session_id,
            "landscape_manifest_path": str(session.landscape_manifest_path),
            "visual_root": None if session.visual_root is None else str(session.visual_root),
            "selected_landscape_example_count": len(session.runs),
            "runs": [
                {
                    "key": run.key,
                    "runtime_family": run.runtime_family,
                    "checkpoint_count_loaded": run.checkpoint_count_loaded,
                    "primitive_counts_by_type": dict(run.primitive_counts_by_type),
                    "landscape_relationship_counts": dict(run.landscape_relationship_counts),
                    "motion_record_counts": dict(run.observer_record_counts),
                    "motion_relationship_counts": {
                        observer: _relationship_counts(relationships)
                        for observer, relationships in run.observer_relationships.items()
                    },
                    "visual_notes": list(run.visual_notes),
                    "motion_report_dir": str(run.motion_report_dir),
                }
                for run in session.runs
            ],
        }
    )


def _summary_markdown(session: MotionLandscapeBridgeSession) -> str:
    lines = [
        "# Landscape Motion Summary",
        "",
        f"- session: `{session.session_id}`",
        f"- version: `{MOTION_LANDSCAPE_BRIDGE_SESSION_VERSION}`",
        f"- landscape manifest: `{session.landscape_manifest_path}`",
        f"- visual root: `{session.visual_root}`",
        "",
        "## Runs",
        "",
    ]
    for run in session.runs:
        lines.extend(
            [
                f"### {run.key}",
                "",
                f"- runtime family: `{run.runtime_family}`",
                f"- checkpoints: `{run.checkpoint_count_loaded}`",
                f"- landscape primitives: `{dict(run.primitive_counts_by_type)}`",
                f"- landscape relationships: `{dict(run.landscape_relationship_counts)}`",
                f"- motion record counts: `{dict(run.observer_record_counts)}`",
                f"- motion relationships: `{ {k: _relationship_counts(v) for k, v in run.observer_relationships.items()} }`",
                f"- motion reports: `{run.motion_report_dir}`",
                "",
            ]
        )
    return "\n".join(lines)


def _relationship_counts(relationships: Sequence[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for relationship in relationships:
        counts[str(relationship)] = counts.get(str(relationship), 0) + 1
    return dict(sorted(counts.items()))


def _readme(session: MotionLandscapeBridgeSession) -> str:
    lines = [
        "# Motion Over Landscape Inference",
        "",
        f"- session version: `{MOTION_LANDSCAPE_BRIDGE_SESSION_VERSION}`",
        f"- landscape manifest: `{session.landscape_manifest_path}`",
        f"- selected examples: `{len(session.runs)}`",
        "",
        "This bridge reuses the runtime checkpoint artifacts selected by",
        "landscape inference and applies motion observers to the same evidence.",
        "Landscape primitives remain landscape-inference claims; motion records",
        "remain motion-inference claims.",
        "",
        "## Runs",
        "",
    ]
    for run in session.runs:
        lines.append(
            f"- `{run.key}` ({run.runtime_family}): checkpoints={run.checkpoint_count_loaded}, "
            f"motion_records={sum(run.observer_record_counts.values())}"
        )
    lines.extend(
        [
            "",
            "## Reproduce",
            "",
            "```bash",
            (
                "PYTHONPATH=src python -m pygrc.landscapes.motion_landscape_bridge "
                f"--landscape-manifest {session.landscape_manifest_path} "
                f"--output-root {session.session_root.parent.parent} "
                f"--session-id {session.session_id}"
            ),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _rerun_script(
    *,
    output_root: Path,
    session_id: str,
    manifest_path: Path,
    keys: Sequence[str] | None,
    observers: Sequence[str],
    render_visuals: bool,
    animated: bool,
) -> str:
    command = (
        "PYTHONPATH=src python -m pygrc.landscapes.motion_landscape_bridge "
        f"--landscape-manifest {manifest_path} --output-root {output_root} "
        f"--session-id {session_id}"
    )
    for key in keys or ():
        command += f" --key {key}"
    for observer in observers:
        command += f" --observer {observer}"
    if not render_visuals:
        command += " --no-visuals"
    if render_visuals and not animated:
        command += " --static-only"
    return "#!/usr/bin/env bash\nset -euo pipefail\n" + command + "\n"


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json_dumps(payload), encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--landscape-manifest",
        default=str(DEFAULT_LANDSCAPE_INFERENCE_SESSION_MANIFEST),
        help="Landscape inference session_manifest.json to bridge.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_MOTION_LANDSCAPE_OUTPUT_ROOT),
        help="Motion output root.",
    )
    parser.add_argument("--session-id", default=DEFAULT_MOTION_LANDSCAPE_SESSION_ID)
    parser.add_argument("--key", action="append", default=None, help="Selected landscape key.")
    parser.add_argument(
        "--observer",
        action="append",
        default=None,
        help="Motion observer to run. Defaults to all observers.",
    )
    parser.add_argument("--no-visuals", action="store_true")
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args(argv)
    session = run_motion_landscape_bridge_session(
        landscape_manifest_path=args.landscape_manifest,
        output_root=args.output_root,
        session_id=args.session_id,
        keys=args.key,
        observers=tuple(_OBSERVER_FNS) if args.observer is None else tuple(args.observer),
        render_visuals=not args.no_visuals,
        animated=not args.static_only,
    )
    print(canonical_json_dumps(session.to_mapping()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_LANDSCAPE_INFERENCE_SESSION_MANIFEST",
    "DEFAULT_MOTION_LANDSCAPE_OUTPUT_ROOT",
    "DEFAULT_MOTION_LANDSCAPE_SESSION_ID",
    "MOTION_LANDSCAPE_BRIDGE_SESSION_VERSION",
    "MotionLandscapeBridgeSession",
    "MotionLandscapeRun",
    "run_motion_landscape_bridge_session",
]
