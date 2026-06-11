"""Replayable structural examples for motion inference."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from pygrc.core import canonicalize_json_value
from pygrc.telemetry.io import build_telemetry_artifact_layout, save_telemetry_artifact_pack
from pygrc.telemetry.schema import (
    EventTelemetryRow,
    GraphCheckpointArtifact,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    RunTelemetrySummary,
    StepTelemetryRow,
)

from .motion_boundary import infer_boundary_motion
from .motion_coherence import infer_coherence_motion
from .motion_identity import infer_identity_motion
from .motion_representative import infer_representative_motion
from .motion_topological import infer_topological_motion


MOTION_EXAMPLES_SESSION_VERSION = "motion_examples_iter8_v1"
DEFAULT_MOTION_EXAMPLES_OUTPUT_ROOT = Path("outputs/motion")
DEFAULT_MOTION_EXAMPLES_SESSION_ID = "S0001"

ObserverName = str
ObserverFunction = Callable[[Path], Any]


@dataclass(frozen=True)
class MotionStructuralExampleSpec:
    """One deterministic synthetic telemetry example."""

    example_name: str
    runtime_family: str
    purpose: str
    evidence_scale: str
    checkpoints: tuple[GraphCheckpointArtifact, ...]
    events: tuple[EventTelemetryRow, ...]
    observers: tuple[ObserverName, ...]
    expected_record_kinds: tuple[str, ...]
    negative_control: bool = False
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class MotionStructuralExampleRun:
    """Persisted example run summary."""

    spec: MotionStructuralExampleSpec
    run_dir: Path
    observer_record_counts: Mapping[str, int]
    observer_relationships: Mapping[str, tuple[str, ...]]
    observer_motion_ids: Mapping[str, tuple[str, ...]]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "example_name": self.spec.example_name,
                "runtime_family": self.spec.runtime_family,
                "purpose": self.spec.purpose,
                "evidence_scale": self.spec.evidence_scale,
                "negative_control": self.spec.negative_control,
                "run_dir": str(self.run_dir),
                "observer_record_counts": dict(self.observer_record_counts),
                "observer_relationships": {
                    key: list(value) for key, value in self.observer_relationships.items()
                },
                "observer_motion_ids": {
                    key: list(value) for key, value in self.observer_motion_ids.items()
                },
                "expected_record_kinds": list(self.spec.expected_record_kinds),
                "notes": list(self.spec.notes),
            }
        )


@dataclass(frozen=True)
class MotionStructuralExamplesSession:
    """Iteration 8 structural example session."""

    session_id: str
    session_root: Path
    runs: tuple[MotionStructuralExampleRun, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "session_version": MOTION_EXAMPLES_SESSION_VERSION,
                "session_id": self.session_id,
                "session_root": str(self.session_root),
                "example_count": len(self.runs),
                "examples": [run.to_mapping() for run in self.runs],
            }
        )


def run_motion_structural_examples(
    *,
    output_root: str | Path = DEFAULT_MOTION_EXAMPLES_OUTPUT_ROOT,
    session_id: str = DEFAULT_MOTION_EXAMPLES_SESSION_ID,
    example_names: Sequence[str] | None = None,
) -> MotionStructuralExamplesSession:
    """Build telemetry examples, run motion observers, and write reports."""

    root = Path(output_root)
    session_root = root / "sessions" / session_id
    session_root.mkdir(parents=True, exist_ok=True)
    specs = default_motion_structural_example_specs()
    selected = _select_examples(specs, example_names)
    runs = tuple(_run_example(session_root, spec) for spec in selected)
    session = MotionStructuralExamplesSession(
        session_id=session_id,
        session_root=session_root,
        runs=runs,
    )
    _write_json(session_root / "session_manifest.json", _session_manifest(session))
    _write_json(session_root / "run_report.json", session.to_mapping())
    _write_text(session_root / "README.md", _readme(session))
    _write_text(session_root / "rerun.sh", _rerun_script(session, output_root=root))
    _write_experimental_log(root / "ExperimentalLog.md", session)
    return session


def default_motion_structural_example_specs() -> tuple[MotionStructuralExampleSpec, ...]:
    """Return the deterministic Iteration 8 structural example suite."""

    return (
        _coherence_transfer_example(),
        _representative_drift_example(),
        _identity_walking_example(),
        _identity_split_example(),
        _identity_merge_example(),
        _identity_collapse_example(),
        _grc9_port_frontier_example(),
        _grc9v3_hybrid_refinement_example(),
        _grc9v3_column_coarse_diagnostic_example(),
        _no_motion_negative_control(),
    )


def _run_example(
    session_root: Path,
    spec: MotionStructuralExampleSpec,
) -> MotionStructuralExampleRun:
    run_dir = session_root / "runs" / spec.example_name
    run_dir.mkdir(parents=True, exist_ok=True)
    layout = build_telemetry_artifact_layout(
        spec.checkpoints[0].identity.run_id,
        root_dir=run_dir,
    )
    save_telemetry_artifact_pack(
        layout,
        step_rows=_step_rows(spec),
        event_rows=spec.events,
        run_summary=_run_summary(spec),
        graph_checkpoint_index=_checkpoint_index(spec),
        graph_checkpoints=spec.checkpoints,
    )
    report_dir = run_dir / "motion_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    record_counts: dict[str, int] = {}
    relationships: dict[str, tuple[str, ...]] = {}
    motion_ids: dict[str, tuple[str, ...]] = {}
    for observer_name in spec.observers:
        result = _observer(observer_name)(layout.run_dir)
        report = result.to_report(
            source_session_id=spec.example_name,
            source_artifact_paths=(str(layout.run_dir),),
        )
        _write_json(report_dir / f"{observer_name}_report.json", report.to_mapping())
        _write_json(report_dir / f"{observer_name}_summary.json", result.to_summary_mapping())
        records = tuple(result.records)
        record_counts[observer_name] = len(records)
        relationships[observer_name] = tuple(record.relationship for record in records)
        motion_ids[observer_name] = tuple(record.motion_id for record in records)
    _write_json(run_dir / "example_manifest.json", _example_manifest(spec, layout.run_dir))
    _write_text(run_dir / "README.md", _example_readme(spec, record_counts, relationships))
    return MotionStructuralExampleRun(
        spec=spec,
        run_dir=layout.run_dir,
        observer_record_counts=dict(sorted(record_counts.items())),
        observer_relationships=dict(sorted(relationships.items())),
        observer_motion_ids=dict(sorted(motion_ids.items())),
    )


def _observer(name: ObserverName) -> ObserverFunction:
    observers: dict[str, ObserverFunction] = {
        "coherence": infer_coherence_motion,
        "representative": infer_representative_motion,
        "identity": infer_identity_motion,
        "boundary": infer_boundary_motion,
        "topological": infer_topological_motion,
    }
    if name not in observers:
        raise ValueError(f"unknown motion observer: {name}")
    return observers[name]


def _coherence_transfer_example() -> MotionStructuralExampleSpec:
    identity = _identity("coherence_transfer_control", "grcv3", 2)
    checkpoints = (
        _checkpoint(
            identity,
            "grcv3",
            checkpoint_id="checkpoint_0000",
            step_index=0,
            nodes=(
                {"node_id": 1, "coherence": 2.0},
                {"node_id": 2, "coherence": 0.5},
            ),
            edges=({"edge_id": 12, "source_node_id": 1, "target_node_id": 2, "signed_flux": 1.0},),
        ),
        _checkpoint(
            identity,
            "grcv3",
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=(
                {"node_id": 1, "coherence": 1.0},
                {"node_id": 2, "coherence": 1.5},
            ),
            edges=({"edge_id": 12, "source_node_id": 1, "target_node_id": 2, "signed_flux": 1.0},),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="coherence_transfer_control",
        runtime_family="grcv3",
        purpose="Pure coherence transfer across an edge without an identity-motion claim.",
        evidence_scale="fine_graph",
        checkpoints=checkpoints,
        events=(),
        observers=("coherence",),
        expected_record_kinds=("coherence",),
    )


def _representative_drift_example() -> MotionStructuralExampleSpec:
    identity = _identity("representative_drift_control", "grcv3", 2)
    checkpoints = (
        _checkpoint(
            identity,
            "grcv3",
            checkpoint_id="checkpoint_0000",
            step_index=0,
            nodes=(
                {"node_id": 1, "coherence": 2.0, "basin_id": "basin_alpha"},
                {"node_id": 2, "coherence": 0.5, "basin_id": "basin_alpha"},
            ),
        ),
        _checkpoint(
            identity,
            "grcv3",
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=(
                {"node_id": 1, "coherence": 0.5, "basin_id": "basin_alpha"},
                {"node_id": 2, "coherence": 2.0, "basin_id": "basin_alpha"},
            ),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="representative_drift_control",
        runtime_family="grcv3",
        purpose="Representative changes within the same basin; identity walking is not claimed.",
        evidence_scale="fine_graph",
        checkpoints=checkpoints,
        events=(),
        observers=("representative",),
        expected_record_kinds=("representative",),
    )


def _identity_walking_example() -> MotionStructuralExampleSpec:
    identity = _identity("identity_walking_control", "grc9v3", 2)
    checkpoints = (
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0000",
            step_index=0,
            nodes=(
                {
                    "node_id": 1,
                    "coherence": 2.0,
                    "basin_id": "basin_old",
                    "is_sink": True,
                    "payload": {
                        "successor_node_id": 2,
                        "hierarchy_parent": "motion_parent",
                        "source_construct_id": "identity_motion_alpha",
                    },
                },
            ),
            edges=({"edge_id": 12, "source_node_id": 1, "target_node_id": 2, "signed_flux": 1.0},),
        ),
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=(
                {
                    "node_id": 2,
                    "coherence": 2.0,
                    "basin_id": "basin_new",
                    "is_sink": True,
                    "payload": {
                        "hierarchy_parent": "motion_parent",
                        "source_construct_id": "identity_motion_alpha",
                    },
                },
            ),
            edges=({"edge_id": 12, "source_node_id": 1, "target_node_id": 2, "signed_flux": 1.0},),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="identity_walking_control",
        runtime_family="grc9v3",
        purpose="Identity continuity walks from one carrier to another with flux, successor, and provenance support.",
        evidence_scale="fine_graph",
        checkpoints=checkpoints,
        events=(),
        observers=("identity",),
        expected_record_kinds=("identity",),
    )


def _identity_split_example() -> MotionStructuralExampleSpec:
    identity = _identity("identity_split_control", "grc9v3", 2)
    checkpoints = (
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0000",
            step_index=0,
            nodes=(
                {
                    "node_id": 1,
                    "coherence": 2.0,
                    "basin_id": "basin_parent",
                    "is_sink": True,
                    "payload": {"successor_node_id": 2},
                },
            ),
            edges=(
                {"edge_id": 12, "source_node_id": 1, "target_node_id": 2, "signed_flux": 1.0},
                {"edge_id": 13, "source_node_id": 1, "target_node_id": 3, "signed_flux": 1.0},
            ),
        ),
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=(
                {"node_id": 2, "coherence": 1.0, "basin_id": "basin_child_a", "is_sink": True},
                {"node_id": 3, "coherence": 1.0, "basin_id": "basin_child_b", "is_sink": True},
            ),
            edges=(
                {"edge_id": 12, "source_node_id": 1, "target_node_id": 2, "signed_flux": 1.0},
                {"edge_id": 13, "source_node_id": 1, "target_node_id": 3, "signed_flux": 1.0},
            ),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="identity_split_control",
        runtime_family="grc9v3",
        purpose="One identity candidate branches into two child carriers.",
        evidence_scale="fine_graph",
        checkpoints=checkpoints,
        events=(_event(identity, "grc9v3", "identity_fission", payload={"node_id": 1}),),
        observers=("identity", "topological"),
        expected_record_kinds=("identity", "topological"),
    )


def _identity_merge_example() -> MotionStructuralExampleSpec:
    identity = _identity("identity_merge_control", "grc9v3", 2)
    checkpoints = (
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0000",
            step_index=0,
            nodes=(
                {"node_id": 1, "coherence": 1.0, "basin_id": "basin_a", "is_sink": True},
                {"node_id": 2, "coherence": 1.0, "basin_id": "basin_b", "is_sink": True},
            ),
            edges=(
                {"edge_id": 14, "source_node_id": 1, "target_node_id": 4, "signed_flux": 1.0},
                {"edge_id": 24, "source_node_id": 2, "target_node_id": 4, "signed_flux": 1.0},
            ),
        ),
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=({"node_id": 4, "coherence": 2.0, "basin_id": "basin_merged", "is_sink": True},),
            edges=(
                {"edge_id": 14, "source_node_id": 1, "target_node_id": 4, "signed_flux": 1.0},
                {"edge_id": 24, "source_node_id": 2, "target_node_id": 4, "signed_flux": 1.0},
            ),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="identity_merge_control",
        runtime_family="grc9v3",
        purpose="Two identity candidates merge into one successor carrier with conserved mass.",
        evidence_scale="fine_graph",
        checkpoints=checkpoints,
        events=(_event(identity, "grc9v3", "merge", payload={"node_id": 4}),),
        observers=("identity", "topological"),
        expected_record_kinds=("identity", "topological"),
    )


def _identity_collapse_example() -> MotionStructuralExampleSpec:
    identity = _identity("identity_collapse_control", "grc9v3", 2)
    checkpoints = (
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0000",
            step_index=0,
            nodes=(
                {"node_id": 1, "coherence": 1.0, "basin_id": "basin_a", "is_sink": True},
                {"node_id": 2, "coherence": 1.0, "basin_id": "basin_b", "is_sink": True},
            ),
            edges=(
                {"edge_id": 15, "source_node_id": 1, "target_node_id": 5, "signed_flux": 1.0},
                {"edge_id": 25, "source_node_id": 2, "target_node_id": 5, "signed_flux": 1.0},
            ),
        ),
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=({"node_id": 5, "coherence": 0.5, "basin_id": "basin_collapsed", "is_sink": True},),
            edges=(
                {"edge_id": 15, "source_node_id": 1, "target_node_id": 5, "signed_flux": 1.0},
                {"edge_id": 25, "source_node_id": 2, "target_node_id": 5, "signed_flux": 1.0},
            ),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="identity_collapse_control",
        runtime_family="grc9v3",
        purpose="Two identity candidates contract into a low-mass successor carrier.",
        evidence_scale="fine_graph",
        checkpoints=checkpoints,
        events=(_event(identity, "grc9v3", "collapse", payload={"node_id": 5}),),
        observers=("identity", "topological"),
        expected_record_kinds=("identity", "topological"),
    )


def _grc9_port_frontier_example() -> MotionStructuralExampleSpec:
    identity = _identity("grc9_port_frontier_motion", "grc9", 2)
    checkpoints = (
        _checkpoint(
            identity,
            "grc9",
            checkpoint_id="checkpoint_0000",
            step_index=0,
            nodes=({"node_id": 1, "coherence": 1.0, "occupied_ports": [1, 2]},),
        ),
        _checkpoint(
            identity,
            "grc9",
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=({"node_id": 1, "coherence": 1.0, "occupied_ports": [1, 2, 3]},),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="grc9_port_frontier_motion",
        runtime_family="grc9",
        purpose="GRC9 port-frontier advance from occupied-port gain.",
        evidence_scale="fine_graph_port_overlay",
        checkpoints=checkpoints,
        events=(),
        observers=("boundary",),
        expected_record_kinds=("boundary",),
    )


def _grc9v3_hybrid_refinement_example() -> MotionStructuralExampleSpec:
    identity = _identity("grc9v3_hybrid_refinement_motion", "grc9v3", 2)
    checkpoints = (
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0000",
            step_index=0,
            nodes=({"node_id": 1, "coherence": 2.0, "occupied_ports": [1, 2, 3, 4, 5, 6, 7, 8, 9]},),
        ),
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=(
                {"node_id": 1, "coherence": 0.0, "occupied_ports": [1, 2, 3]},
                {"node_id": 2, "coherence": 0.7, "occupied_ports": [1]},
                {"node_id": 3, "coherence": 0.7, "occupied_ports": [1]},
                {"node_id": 4, "coherence": 0.6, "occupied_ports": [1]},
            ),
            edges=(
                {"edge_id": 12, "source_node_id": 1, "target_node_id": 2, "signed_flux": 0.5},
                {"edge_id": 13, "source_node_id": 1, "target_node_id": 3, "signed_flux": 0.5},
                {"edge_id": 14, "source_node_id": 1, "target_node_id": 4, "signed_flux": 0.5},
            ),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="grc9v3_hybrid_refinement_motion",
        runtime_family="grc9v3",
        purpose="Hybrid spark/expansion support refinement with new module carriers.",
        evidence_scale="fine_graph_port_overlay",
        checkpoints=checkpoints,
        events=(_event(identity, "grc9v3", "hybrid_mechanical_expansion", payload={"node_id": 1}),),
        observers=("boundary", "topological"),
        expected_record_kinds=("boundary", "topological"),
    )


def _grc9v3_column_coarse_diagnostic_example() -> MotionStructuralExampleSpec:
    identity = _identity("grc9v3_column_coarse_motion_diagnostic", "grc9v3", 2)
    checkpoints = (
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0000",
            step_index=0,
            nodes=(
                {
                    "node_id": 1,
                    "coherence": 1.0,
                    "occupied_ports": [2, 5],
                    "payload": {"coarse_evidence_level": "column_coarse", "coarse_column": 2},
                },
            ),
        ),
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=(
                {
                    "node_id": 1,
                    "coherence": 1.0,
                    "occupied_ports": [2, 5, 8],
                    "payload": {"coarse_evidence_level": "column_coarse", "coarse_column": 2},
                },
            ),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="grc9v3_column_coarse_motion_diagnostic",
        runtime_family="grc9v3",
        purpose="Column-coarse diagnostic for port-frontier motion evidence.",
        evidence_scale="column_coarse_diagnostic",
        checkpoints=checkpoints,
        events=(),
        observers=("boundary",),
        expected_record_kinds=("boundary",),
        notes=("column-coarse metadata is diagnostic; observer still uses checkpoint-local port overlays",),
    )


def _no_motion_negative_control() -> MotionStructuralExampleSpec:
    identity = _identity("no_motion_negative_control", "grcv3", 2)
    nodes = (
        {"node_id": 1, "coherence": 1.0, "basin_id": "stable", "is_sink": True},
        {"node_id": 2, "coherence": 0.5, "basin_id": "stable"},
    )
    checkpoints = (
        _checkpoint(
            identity,
            "grcv3",
            checkpoint_id="checkpoint_0000",
            step_index=0,
            nodes=nodes,
        ),
        _checkpoint(
            identity,
            "grcv3",
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=nodes,
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="no_motion_negative_control",
        runtime_family="grcv3",
        purpose="Negative control with stable checkpoint-local surfaces.",
        evidence_scale="fine_graph",
        checkpoints=checkpoints,
        events=(),
        observers=("coherence", "representative", "identity", "boundary", "topological"),
        expected_record_kinds=(),
        negative_control=True,
        notes=("identity observer may emit stationary records; non-stationary motion should remain absent",),
    )


def _identity(seed_name: str, family: str, steps: int) -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id=f"{family}_{seed_name}",
        model_family=family,
        params_identity="motion_examples",
        seed_name=seed_name,
        seed_source_reference="motion_examples_iter8_synthetic_checkpoint_series",
        requested_steps=steps,
    )


def _checkpoint(
    identity: RunTelemetryIdentity,
    family: str,
    *,
    checkpoint_id: str,
    step_index: int,
    nodes: tuple[dict[str, object], ...],
    edges: tuple[dict[str, object], ...] = (),
) -> GraphCheckpointArtifact:
    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index),
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="motion_examples_iter8",
        graph_kind="weighted_graph",
        node_count=len(nodes),
        edge_count=len(edges),
        node_records=nodes,
        edge_records=edges,
        family_extensions={
            family: {
                "contract_version": "motion_examples_iter8",
                "evidence_source": "synthetic_checkpoint_series",
            }
        },
    )


def _event(
    identity: RunTelemetryIdentity,
    family: str,
    kind: str,
    *,
    payload: Mapping[str, object] | None = None,
    step_index: int = 1,
) -> EventTelemetryRow:
    payload_dict = {} if payload is None else dict(payload)
    return EventTelemetryRow(
        identity=identity,
        step_index=step_index,
        event_index=0,
        event_kind=kind,
        source_family=family,
        payload=payload_dict,
        family_extensions={
            family: {
                "contract_version": "motion_examples_iter8",
                "event_domain": kind,
                "lifecycle_stage": "completed",
                "topology_mutation": True,
                "primary_node_id": payload_dict.get("node_id"),
            }
        },
    )


def _step_rows(spec: MotionStructuralExampleSpec) -> tuple[StepTelemetryRow, ...]:
    event_counts_by_step = Counter(event.step_index for event in spec.events)
    return tuple(
        StepTelemetryRow(
            identity=spec.checkpoints[0].identity,
            step_index=checkpoint.step_index,
            time=checkpoint.time,
            event_count=event_counts_by_step.get(checkpoint.step_index, 0),
            event_counts_by_kind=dict(
                Counter(
                    event.event_kind
                    for event in spec.events
                    if event.step_index == checkpoint.step_index
                )
            ),
            observables={},
            family_extensions={
                spec.runtime_family: {
                    "contract_version": "motion_examples_iter8",
                    "evidence_scale": spec.evidence_scale,
                }
            },
        )
        for checkpoint in spec.checkpoints
    )


def _run_summary(spec: MotionStructuralExampleSpec) -> RunTelemetrySummary:
    identity = spec.checkpoints[0].identity
    event_counts = Counter(event.event_kind for event in spec.events)
    return RunTelemetrySummary(
        identity=identity,
        completed_steps=max(checkpoint.step_index for checkpoint in spec.checkpoints) + 1,
        final_step_index=max(checkpoint.step_index for checkpoint in spec.checkpoints),
        initial_time=float(spec.checkpoints[0].time),
        final_time=float(spec.checkpoints[-1].time),
        total_event_count=len(spec.events),
        event_counts_by_kind=dict(sorted(event_counts.items())),
        initial_observables={},
        final_observables={},
        resolved_params={},
        raw_params={},
        parameter_overrides={},
        status="completed",
        family_extensions={
            spec.runtime_family: {
                "contract_version": "motion_examples_iter8",
                "evidence_scale": spec.evidence_scale,
                "example_name": spec.example_name,
            }
        },
    )


def _checkpoint_index(spec: MotionStructuralExampleSpec) -> GraphCheckpointIndex:
    identity = spec.checkpoints[0].identity
    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="motion_examples_iter8_all_checkpoints",
        selection_params={"example_name": spec.example_name},
        checkpoints=tuple(
            GraphCheckpointReference(
                checkpoint_id=checkpoint.checkpoint_id,
                step_index=checkpoint.step_index,
                time=checkpoint.time,
                checkpoint_label=checkpoint.checkpoint_label,
                path=f"{checkpoint.checkpoint_id}.json",
            )
            for checkpoint in spec.checkpoints
        ),
    )


def _example_manifest(spec: MotionStructuralExampleSpec, run_dir: Path) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "session_version": MOTION_EXAMPLES_SESSION_VERSION,
            "example_name": spec.example_name,
            "runtime_family": spec.runtime_family,
            "purpose": spec.purpose,
            "evidence_scale": spec.evidence_scale,
            "run_dir": str(run_dir),
            "observers": list(spec.observers),
            "expected_record_kinds": list(spec.expected_record_kinds),
            "negative_control": spec.negative_control,
            "notes": list(spec.notes),
        }
    )


def _session_manifest(session: MotionStructuralExamplesSession) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "session_version": MOTION_EXAMPLES_SESSION_VERSION,
            "session_id": session.session_id,
            "session_root": str(session.session_root),
            "example_count": len(session.runs),
            "examples": [
                {
                    "example_name": run.spec.example_name,
                    "runtime_family": run.spec.runtime_family,
                    "evidence_scale": run.spec.evidence_scale,
                    "run_dir": str(run.run_dir),
                    "observers": list(run.spec.observers),
                    "rerun_command": (
                        "PYTHONPATH=src python -m pygrc.landscapes.motion_examples "
                        f"--output-root {session.session_root.parent.parent} "
                        f"--session-id {session.session_id} "
                        f"--example {run.spec.example_name}"
                    ),
                }
                for run in session.runs
            ],
        }
    )


def _example_readme(
    spec: MotionStructuralExampleSpec,
    record_counts: Mapping[str, int],
    relationships: Mapping[str, tuple[str, ...]],
) -> str:
    lines = [
        f"# {spec.example_name}",
        "",
        spec.purpose,
        "",
        f"- runtime family: `{spec.runtime_family}`",
        f"- evidence scale: `{spec.evidence_scale}`",
        f"- negative control: `{spec.negative_control}`",
        "",
        "## Observer Results",
        "",
    ]
    for observer in spec.observers:
        lines.append(
            f"- `{observer}`: {record_counts.get(observer, 0)} records, "
            f"relationships `{list(relationships.get(observer, ()))}`"
        )
    if spec.notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in spec.notes)
    lines.append("")
    return "\n".join(lines)


def _readme(session: MotionStructuralExamplesSession) -> str:
    lines = [
        f"# Motion Structural Examples {session.session_id}",
        "",
        "Iteration 8 structural examples for motion inference.",
        "",
        "These examples are synthetic telemetry/checkpoint fixtures. They are",
        "runtime evidence surfaces for motion observers, not source-authored",
        "claims that motion happened.",
        "",
        "## Examples",
        "",
    ]
    for run in session.runs:
        lines.append(
            f"- `{run.spec.example_name}` ({run.spec.runtime_family}, "
            f"{run.spec.evidence_scale}): {run.spec.purpose}"
        )
    lines.extend(
        [
            "",
            "## Rerun",
            "",
            "```bash",
            f"PYTHONPATH=src python -m pygrc.landscapes.motion_examples --output-root {session.session_root.parent.parent} --session-id {session.session_id}",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _rerun_script(session: MotionStructuralExamplesSession, *, output_root: Path) -> str:
    return "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            f"PYTHONPATH=src python -m pygrc.landscapes.motion_examples --output-root {output_root} --session-id {session.session_id}",
            "",
        ]
    )


def _write_experimental_log(path: Path, session: MotionStructuralExamplesSession) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Motion Experimental Log",
        "",
        f"## {session.session_id}",
        "",
        f"- session version: `{MOTION_EXAMPLES_SESSION_VERSION}`",
        f"- session root: `{session.session_root}`",
        f"- examples: `{len(session.runs)}`",
        "",
    ]
    for run in session.runs:
        lines.append(
            f"- `{run.spec.example_name}`: observers `{list(run.spec.observers)}`, "
            f"records `{dict(run.observer_record_counts)}`"
        )
    lines.append("")
    _write_text(path, "\n".join(lines))


def _select_examples(
    specs: Sequence[MotionStructuralExampleSpec],
    example_names: Sequence[str] | None,
) -> tuple[MotionStructuralExampleSpec, ...]:
    if not example_names:
        return tuple(specs)
    by_name = {spec.example_name: spec for spec in specs}
    missing = tuple(name for name in example_names if name not in by_name)
    if missing:
        raise ValueError(f"unknown motion example(s): {', '.join(missing)}")
    return tuple(by_name[name] for name in example_names)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(canonicalize_json_value(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run motion structural examples.")
    parser.add_argument("--output-root", default=str(DEFAULT_MOTION_EXAMPLES_OUTPUT_ROOT))
    parser.add_argument("--session-id", default=DEFAULT_MOTION_EXAMPLES_SESSION_ID)
    parser.add_argument(
        "--example",
        action="append",
        dest="examples",
        help="Example name to run. May be provided multiple times. Defaults to all examples.",
    )
    args = parser.parse_args(argv)
    session = run_motion_structural_examples(
        output_root=args.output_root,
        session_id=args.session_id,
        example_names=args.examples,
    )
    print(json.dumps(session.to_mapping(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_MOTION_EXAMPLES_OUTPUT_ROOT",
    "DEFAULT_MOTION_EXAMPLES_SESSION_ID",
    "MOTION_EXAMPLES_SESSION_VERSION",
    "MotionStructuralExampleRun",
    "MotionStructuralExampleSpec",
    "MotionStructuralExamplesSession",
    "default_motion_structural_example_specs",
    "run_motion_structural_examples",
]
