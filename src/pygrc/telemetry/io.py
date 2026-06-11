"""Deterministic artifact layout and I/O helpers for telemetry payloads."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from pygrc.core import canonical_json_dumps, canonicalize_json_value

from .schema import (
    EventTelemetryRow,
    GraphCheckpointArtifact,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    RunTelemetrySummary,
    StepTelemetryRow,
    TelemetryComparisonReport,
    TelemetryExperimentReport,
)


DEFAULT_OUTPUTS_ROOT = Path("outputs")
DEFAULT_EXPERIMENTS_ROOT = DEFAULT_OUTPUTS_ROOT
DEFAULT_TELEMETRY_ROOT = DEFAULT_EXPERIMENTS_ROOT
TELEMETRY_DIRNAME = "telemetry"
STEP_ROWS_FILENAME = "steps.jsonl"
EVENT_ROWS_FILENAME = "events.jsonl"
RUN_SUMMARY_FILENAME = "run_summary.json"
COMPARISON_REPORT_FILENAME = "comparison_report.json"
EXPERIMENT_REPORT_FILENAME = "experiment_report.json"
GRAPH_CHECKPOINTS_DIRNAME = "graph_checkpoints"
GRAPH_CHECKPOINT_INDEX_FILENAME = "index.json"
GRAPH_CHECKPOINT_CHUNK_PREFIX = "chunk-"
GRAPH_CHECKPOINT_CHUNK_SUFFIX = ".jsonl"


class TelemetryArtifactError(ValueError):
    """Raised when a telemetry artifact cannot be encoded or decoded strictly."""


@dataclass(frozen=True)
class TelemetryArtifactLayout:
    """Deterministic run-directory layout for one telemetry artifact pack."""

    root_dir: Path
    run_id: str
    run_dir: Path
    telemetry_dir: Path
    step_rows_path: Path
    event_rows_path: Path
    run_summary_path: Path
    comparison_report_path: Path
    experiment_report_path: Path
    graph_checkpoints_dir: Path
    graph_checkpoint_index_path: Path


@dataclass(frozen=True)
class TelemetryArtifactPack:
    """Loadable telemetry artifact pack for one run directory."""

    layout: TelemetryArtifactLayout
    step_rows: tuple[StepTelemetryRow, ...]
    event_rows: tuple[EventTelemetryRow, ...]
    run_summary: RunTelemetrySummary
    experiment_report: TelemetryExperimentReport | None = None
    comparison_report: TelemetryComparisonReport | None = None
    graph_checkpoint_index: GraphCheckpointIndex | None = None
    graph_checkpoints: tuple[GraphCheckpointArtifact, ...] = ()


@dataclass
class GraphCheckpointChunkWriter:
    """Append-only chunked writer for dense graph checkpoint persistence."""

    layout: TelemetryArtifactLayout
    chunk_size: int = 100
    _current_chunk_index: int = 0
    _entries_in_current_chunk: int = 0

    def __post_init__(self) -> None:
        if self.chunk_size <= 0:
            raise TelemetryArtifactError("chunk_size must be > 0 for graph checkpoint chunking")
        if self.layout.graph_checkpoints_dir.exists():
            for child in self.layout.graph_checkpoints_dir.iterdir():
                if child.is_file():
                    child.unlink()
        else:
            self.layout.graph_checkpoints_dir.mkdir(parents=True, exist_ok=True)

    def write(self, checkpoint: GraphCheckpointArtifact) -> GraphCheckpointReference:
        """Append one checkpoint and return its chunk-backed reference."""

        if self._current_chunk_index == 0 or self._entries_in_current_chunk >= self.chunk_size:
            self._current_chunk_index += 1
            self._entries_in_current_chunk = 0
        chunk_path = build_graph_checkpoint_chunk_path(self.layout, self._current_chunk_index)
        line_index = self._entries_in_current_chunk
        _append_jsonl_line(chunk_path, _graph_checkpoint_to_json(checkpoint))
        self._entries_in_current_chunk += 1
        return GraphCheckpointReference(
            checkpoint_id=checkpoint.checkpoint_id,
            step_index=checkpoint.step_index,
            time=checkpoint.time,
            checkpoint_label=checkpoint.checkpoint_label,
            checkpoint_reason=checkpoint.checkpoint_reason,
            path=chunk_path.name,
            storage_kind="jsonl_chunk",
            chunk_line_index=line_index,
            event_step_range=checkpoint.event_step_range,
            event_count_window=checkpoint.event_count_window,
            event_counts_by_kind_window=checkpoint.event_counts_by_kind_window,
        )


def build_telemetry_artifact_layout(
    run_id: str,
    *,
    root_dir: str | Path = DEFAULT_TELEMETRY_ROOT,
    experiment_path: str | Path | None = None,
) -> TelemetryArtifactLayout:
    """Build the deterministic artifact layout for one telemetry run."""

    if not isinstance(run_id, str) or not run_id.strip():
        raise TelemetryArtifactError("run_id must be a non-empty string")
    base_dir = resolve_telemetry_root(root_dir=root_dir, experiment_path=experiment_path)
    run_dir = base_dir / run_id
    telemetry_dir = run_dir / TELEMETRY_DIRNAME
    return TelemetryArtifactLayout(
        root_dir=base_dir,
        run_id=run_id,
        run_dir=run_dir,
        telemetry_dir=telemetry_dir,
        step_rows_path=telemetry_dir / STEP_ROWS_FILENAME,
        event_rows_path=telemetry_dir / EVENT_ROWS_FILENAME,
        run_summary_path=telemetry_dir / RUN_SUMMARY_FILENAME,
        comparison_report_path=telemetry_dir / COMPARISON_REPORT_FILENAME,
        experiment_report_path=telemetry_dir / EXPERIMENT_REPORT_FILENAME,
        graph_checkpoints_dir=telemetry_dir / GRAPH_CHECKPOINTS_DIRNAME,
        graph_checkpoint_index_path=telemetry_dir
        / GRAPH_CHECKPOINTS_DIRNAME
        / GRAPH_CHECKPOINT_INDEX_FILENAME,
    )


def resolve_telemetry_root(
    *,
    root_dir: str | Path = DEFAULT_TELEMETRY_ROOT,
    experiment_path: str | Path | None = None,
) -> Path:
    """Resolve the effective telemetry root for one experiment lane."""

    base_dir = Path(root_dir)
    if experiment_path is None:
        return base_dir
    if not str(experiment_path).strip():
        raise TelemetryArtifactError("experiment_path must not be empty or whitespace-only")
    relative_path = Path(experiment_path)
    if relative_path == Path("."):
        raise TelemetryArtifactError("experiment_path must not resolve to the current directory")
    if relative_path.is_absolute():
        raise TelemetryArtifactError("experiment_path must be relative")
    if ".." in relative_path.parts:
        raise TelemetryArtifactError("experiment_path must not traverse parent directories")
    return base_dir / relative_path


def _atomic_write_text(path: str | Path, payload: str) -> None:
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=target_path.parent,
        prefix=f".{target_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temp_file:
        temp_file.write(payload)
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_path = Path(temp_file.name)
    os.replace(temp_path, target_path)


def _append_jsonl_line(path: str | Path, payload: Mapping[str, Any]) -> None:
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json_dumps(payload))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def _identity_to_json(identity: RunTelemetryIdentity) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "run_id": identity.run_id,
            "model_family": identity.model_family,
            "params_identity": identity.params_identity,
            "seed_name": identity.seed_name,
            "seed_source_reference": identity.seed_source_reference,
            "seed_path": identity.seed_path,
            "param_family": identity.param_family,
            "rng_seed": identity.rng_seed,
            "requested_steps": identity.requested_steps,
        }
    )


def _identity_from_json(payload: Any) -> RunTelemetryIdentity:
    mapping = _require_mapping(payload, context="telemetry.identity")
    return RunTelemetryIdentity(
        run_id=_require_string(mapping.get("run_id"), context="telemetry.identity.run_id"),
        model_family=_require_string(
            mapping.get("model_family"),
            context="telemetry.identity.model_family",
        ),
        params_identity=_optional_string(
            mapping.get("params_identity"),
            context="telemetry.identity.params_identity",
        ),
        seed_name=_optional_string(mapping.get("seed_name"), context="telemetry.identity.seed_name"),
        seed_source_reference=_optional_string(
            mapping.get("seed_source_reference"),
            context="telemetry.identity.seed_source_reference",
        ),
        seed_path=_optional_string(mapping.get("seed_path"), context="telemetry.identity.seed_path"),
        param_family=_optional_string(
            mapping.get("param_family"),
            context="telemetry.identity.param_family",
        ),
        rng_seed=_optional_int(mapping.get("rng_seed"), context="telemetry.identity.rng_seed"),
        requested_steps=_optional_int(
            mapping.get("requested_steps"),
            context="telemetry.identity.requested_steps",
        ),
    )


def _step_row_to_json(row: StepTelemetryRow) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "identity": _identity_to_json(row.identity),
            "step_index": row.step_index,
            "time": row.time,
            "event_count": row.event_count,
            "event_counts_by_kind": row.event_counts_by_kind,
            "observables": row.observables,
            "bookkeeping": row.bookkeeping,
            "family_extensions": row.family_extensions,
        }
    )


def _step_row_from_json(payload: Any) -> StepTelemetryRow:
    mapping = _require_mapping(payload, context="step telemetry row")
    return StepTelemetryRow(
        identity=_identity_from_json(mapping.get("identity")),
        step_index=_require_int(mapping.get("step_index"), context="step telemetry row.step_index"),
        time=_require_float(mapping.get("time"), context="step telemetry row.time"),
        event_count=_require_int(mapping.get("event_count"), context="step telemetry row.event_count"),
        event_counts_by_kind=_require_string_keyed_int_mapping(
            mapping.get("event_counts_by_kind", {}),
            context="step telemetry row.event_counts_by_kind",
        ),
        observables=_require_string_keyed_mapping(
            mapping.get("observables"),
            context="step telemetry row.observables",
        ),
        bookkeeping=_require_string_keyed_mapping(
            mapping.get("bookkeeping", {}),
            context="step telemetry row.bookkeeping",
        ),
        family_extensions=_require_family_extensions(
            mapping.get("family_extensions", {}),
            context="step telemetry row.family_extensions",
        ),
    )


def _event_row_to_json(row: EventTelemetryRow) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "identity": _identity_to_json(row.identity),
            "step_index": row.step_index,
            "event_index": row.event_index,
            "event_kind": row.event_kind,
            "source_family": row.source_family,
            "payload": row.payload,
            "family_extensions": row.family_extensions,
        }
    )


def _event_row_from_json(payload: Any) -> EventTelemetryRow:
    mapping = _require_mapping(payload, context="event telemetry row")
    return EventTelemetryRow(
        identity=_identity_from_json(mapping.get("identity")),
        step_index=_require_int(mapping.get("step_index"), context="event telemetry row.step_index"),
        event_index=_require_int(mapping.get("event_index"), context="event telemetry row.event_index"),
        event_kind=_require_string(mapping.get("event_kind"), context="event telemetry row.event_kind"),
        source_family=_optional_string(
            mapping.get("source_family"),
            context="event telemetry row.source_family",
        ),
        payload=_require_string_keyed_mapping(
            mapping.get("payload", {}),
            context="event telemetry row.payload",
        ),
        family_extensions=_require_family_extensions(
            mapping.get("family_extensions", {}),
            context="event telemetry row.family_extensions",
        ),
    )


def _run_summary_to_json(summary: RunTelemetrySummary) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "identity": _identity_to_json(summary.identity),
            "completed_steps": summary.completed_steps,
            "final_step_index": summary.final_step_index,
            "initial_time": summary.initial_time,
            "final_time": summary.final_time,
            "total_event_count": summary.total_event_count,
            "event_counts_by_kind": summary.event_counts_by_kind,
            "initial_observables": summary.initial_observables,
            "final_observables": summary.final_observables,
            "resolved_params": summary.resolved_params,
            "raw_params": summary.raw_params,
            "parameter_overrides": summary.parameter_overrides,
            "status": summary.status,
            "family_extensions": summary.family_extensions,
        }
    )


def _run_summary_from_json(payload: Any) -> RunTelemetrySummary:
    mapping = _require_mapping(payload, context="run telemetry summary")
    return RunTelemetrySummary(
        identity=_identity_from_json(mapping.get("identity")),
        completed_steps=_require_int(
            mapping.get("completed_steps"),
            context="run telemetry summary.completed_steps",
        ),
        final_step_index=_require_int(
            mapping.get("final_step_index"),
            context="run telemetry summary.final_step_index",
        ),
        initial_time=_require_float(
            mapping.get("initial_time"),
            context="run telemetry summary.initial_time",
        ),
        final_time=_require_float(
            mapping.get("final_time"),
            context="run telemetry summary.final_time",
        ),
        total_event_count=_require_int(
            mapping.get("total_event_count"),
            context="run telemetry summary.total_event_count",
        ),
        event_counts_by_kind=_require_string_keyed_int_mapping(
            mapping.get("event_counts_by_kind", {}),
            context="run telemetry summary.event_counts_by_kind",
        ),
        initial_observables=_require_string_keyed_mapping(
            mapping.get("initial_observables", {}),
            context="run telemetry summary.initial_observables",
        ),
        final_observables=_require_string_keyed_mapping(
            mapping.get("final_observables", {}),
            context="run telemetry summary.final_observables",
        ),
        resolved_params=_require_string_keyed_mapping(
            mapping.get("resolved_params", {}),
            context="run telemetry summary.resolved_params",
        ),
        raw_params=_require_string_keyed_mapping(
            mapping.get("raw_params", {}),
            context="run telemetry summary.raw_params",
        ),
        parameter_overrides=_require_string_keyed_mapping(
            mapping.get("parameter_overrides", {}),
            context="run telemetry summary.parameter_overrides",
        ),
        status=_require_string(mapping.get("status"), context="run telemetry summary.status"),
        family_extensions=_require_family_extensions(
            mapping.get("family_extensions", {}),
            context="run telemetry summary.family_extensions",
        ),
    )


def _report_to_json(report: TelemetryComparisonReport | TelemetryExperimentReport) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "kind": report.kind,
            "family": report.family,
            "common": report.common,
            "extensions": report.extensions,
        }
    )


def _comparison_report_from_json(payload: Any) -> TelemetryComparisonReport:
    mapping = _require_mapping(payload, context="comparison telemetry report")
    kind = _require_string(mapping.get("kind"), context="comparison telemetry report.kind")
    if kind != "comparison_report":
        raise TelemetryArtifactError(
            f"comparison telemetry report.kind must be 'comparison_report'; got {kind!r}"
        )
    return TelemetryComparisonReport(
        family=_require_string(mapping.get("family"), context="comparison telemetry report.family"),
        common=_require_string_keyed_mapping(
            mapping.get("common", {}),
            context="comparison telemetry report.common",
        ),
        extensions=_require_family_extensions(
            mapping.get("extensions", {}),
            context="comparison telemetry report.extensions",
        ),
    )


def _experiment_report_from_json(payload: Any) -> TelemetryExperimentReport:
    mapping = _require_mapping(payload, context="experiment telemetry report")
    kind = _require_string(mapping.get("kind"), context="experiment telemetry report.kind")
    if kind != "experiment_report":
        raise TelemetryArtifactError(
            f"experiment telemetry report.kind must be 'experiment_report'; got {kind!r}"
        )
    return TelemetryExperimentReport(
        family=_require_string(mapping.get("family"), context="experiment telemetry report.family"),
        common=_require_string_keyed_mapping(
            mapping.get("common", {}),
            context="experiment telemetry report.common",
        ),
        extensions=_require_family_extensions(
            mapping.get("extensions", {}),
            context="experiment telemetry report.extensions",
        ),
    )


def _graph_checkpoint_to_json(checkpoint: GraphCheckpointArtifact) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "artifact_type": "graph_checkpoint",
            "identity": _identity_to_json(checkpoint.identity),
            "checkpoint_id": checkpoint.checkpoint_id,
            "step_index": checkpoint.step_index,
            "time": checkpoint.time,
            "checkpoint_label": checkpoint.checkpoint_label,
            "checkpoint_reason": checkpoint.checkpoint_reason,
            "graph_kind": checkpoint.graph_kind,
            "node_count": checkpoint.node_count,
            "edge_count": checkpoint.edge_count,
            "node_records": checkpoint.node_records,
            "edge_records": checkpoint.edge_records,
            "event_step_range": checkpoint.event_step_range,
            "event_count_window": checkpoint.event_count_window,
            "event_counts_by_kind_window": checkpoint.event_counts_by_kind_window,
            "flow_representation": checkpoint.flow_representation,
            "flow_cadence": checkpoint.flow_cadence,
            "layout_mode": checkpoint.layout_mode,
            "layout_dimensions": checkpoint.layout_dimensions,
            "layout_hints": checkpoint.layout_hints,
            "label_computation_modes": checkpoint.label_computation_modes,
            "topology_extensions": checkpoint.topology_extensions,
            "family_extensions": checkpoint.family_extensions,
        }
    )


def _graph_checkpoint_from_json(payload: Any) -> GraphCheckpointArtifact:
    mapping = _require_mapping(payload, context="graph checkpoint artifact")
    artifact_type = _require_string(
        mapping.get("artifact_type"),
        context="graph checkpoint artifact.artifact_type",
    )
    if artifact_type != "graph_checkpoint":
        raise TelemetryArtifactError(
            f"graph checkpoint artifact.artifact_type must be 'graph_checkpoint'; got {artifact_type!r}"
        )
    graph_kind = _require_string(
        mapping.get("graph_kind"),
        context="graph checkpoint artifact.graph_kind",
    )
    node_records = _require_record_sequence(
        mapping.get("node_records", ()),
        context="graph checkpoint artifact.node_records",
    )
    edge_records = _require_record_sequence(
        mapping.get("edge_records", ()),
        context="graph checkpoint artifact.edge_records",
    )
    for index, record in enumerate(node_records):
        _require_int(record.get("node_id"), context=f"graph checkpoint node_records[{index}].node_id")
    for index, record in enumerate(edge_records):
        _require_int(record.get("edge_id"), context=f"graph checkpoint edge_records[{index}].edge_id")
        if graph_kind == "weighted_graph":
            _require_int(
                record.get("source_node_id"),
                context=f"graph checkpoint edge_records[{index}].source_node_id",
            )
            _require_int(
                record.get("target_node_id"),
                context=f"graph checkpoint edge_records[{index}].target_node_id",
            )
        elif graph_kind == "port_graph":
            _require_int(
                record.get("source_node_id"),
                context=f"graph checkpoint edge_records[{index}].source_node_id",
            )
            _require_int(
                record.get("source_port_id"),
                context=f"graph checkpoint edge_records[{index}].source_port_id",
            )
            _require_int(
                record.get("target_node_id"),
                context=f"graph checkpoint edge_records[{index}].target_node_id",
            )
            _require_int(
                record.get("target_port_id"),
                context=f"graph checkpoint edge_records[{index}].target_port_id",
            )
        else:
            raise TelemetryArtifactError(
                f"graph checkpoint artifact.graph_kind must be 'weighted_graph' or 'port_graph'; got {graph_kind!r}"
            )

    node_count = _require_int(mapping.get("node_count"), context="graph checkpoint artifact.node_count")
    edge_count = _require_int(mapping.get("edge_count"), context="graph checkpoint artifact.edge_count")
    if node_count != len(node_records):
        raise TelemetryArtifactError(
            "graph checkpoint artifact.node_count does not match node_records length"
        )
    if edge_count != len(edge_records):
        raise TelemetryArtifactError(
            "graph checkpoint artifact.edge_count does not match edge_records length"
        )

    return GraphCheckpointArtifact(
        identity=_identity_from_json(mapping.get("identity")),
        checkpoint_id=_require_string(
            mapping.get("checkpoint_id"),
            context="graph checkpoint artifact.checkpoint_id",
        ),
        step_index=_require_int(
            mapping.get("step_index"),
            context="graph checkpoint artifact.step_index",
        ),
        time=_require_float(mapping.get("time"), context="graph checkpoint artifact.time"),
        checkpoint_label=_require_string(
            mapping.get("checkpoint_label"),
            context="graph checkpoint artifact.checkpoint_label",
        ),
        checkpoint_reason=_optional_string(
            mapping.get("checkpoint_reason"),
            context="graph checkpoint artifact.checkpoint_reason",
        ),
        graph_kind=graph_kind,
        node_count=node_count,
        edge_count=edge_count,
        node_records=node_records,
        edge_records=edge_records,
        event_step_range=_require_string_keyed_int_mapping(
            mapping.get("event_step_range", {}),
            context="graph checkpoint artifact.event_step_range",
        ),
        event_count_window=_require_int(
            mapping.get("event_count_window", 0),
            context="graph checkpoint artifact.event_count_window",
        ),
        event_counts_by_kind_window=_require_string_keyed_int_mapping(
            mapping.get("event_counts_by_kind_window", {}),
            context="graph checkpoint artifact.event_counts_by_kind_window",
        ),
        flow_representation=_optional_string(
            mapping.get("flow_representation"),
            context="graph checkpoint artifact.flow_representation",
        ),
        flow_cadence=_optional_string(
            mapping.get("flow_cadence"),
            context="graph checkpoint artifact.flow_cadence",
        ),
        layout_mode=_optional_string(
            mapping.get("layout_mode"),
            context="graph checkpoint artifact.layout_mode",
        ),
        layout_dimensions=_optional_int(
            mapping.get("layout_dimensions"),
            context="graph checkpoint artifact.layout_dimensions",
        ),
        layout_hints=_require_string_keyed_mapping(
            mapping.get("layout_hints", {}),
            context="graph checkpoint artifact.layout_hints",
        ),
        label_computation_modes=_require_string_keyed_mapping(
            mapping.get("label_computation_modes", {}),
            context="graph checkpoint artifact.label_computation_modes",
        ),
        topology_extensions=_require_string_keyed_mapping(
            mapping.get("topology_extensions", {}),
            context="graph checkpoint artifact.topology_extensions",
        ),
        family_extensions=_require_family_extensions(
            mapping.get("family_extensions", {}),
            context="graph checkpoint artifact.family_extensions",
        ),
    )


def _graph_checkpoint_index_to_json(index: GraphCheckpointIndex) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "artifact_type": "graph_checkpoint_index",
            "identity": _identity_to_json(index.identity),
            "selection_policy": index.selection_policy,
            "selection_params": index.selection_params,
            "checkpoints": [
                {
                    "checkpoint_id": reference.checkpoint_id,
                    "step_index": reference.step_index,
                    "time": reference.time,
                    "checkpoint_label": reference.checkpoint_label,
                    "checkpoint_reason": reference.checkpoint_reason,
                    "path": reference.path,
                    "storage_kind": reference.storage_kind,
                    "chunk_line_index": reference.chunk_line_index,
                    "event_step_range": reference.event_step_range,
                    "event_count_window": reference.event_count_window,
                    "event_counts_by_kind_window": reference.event_counts_by_kind_window,
                }
                for reference in index.checkpoints
            ],
            "family_extensions": index.family_extensions,
        }
    )


def _graph_checkpoint_index_from_json(payload: Any) -> GraphCheckpointIndex:
    mapping = _require_mapping(payload, context="graph checkpoint index")
    artifact_type = _require_string(
        mapping.get("artifact_type"),
        context="graph checkpoint index.artifact_type",
    )
    if artifact_type != "graph_checkpoint_index":
        raise TelemetryArtifactError(
            f"graph checkpoint index.artifact_type must be 'graph_checkpoint_index'; got {artifact_type!r}"
        )
    raw_checkpoints = mapping.get("checkpoints", ())
    if not isinstance(raw_checkpoints, Sequence) or isinstance(raw_checkpoints, str | bytes):
        raise TelemetryArtifactError("graph checkpoint index.checkpoints must be a sequence")
    checkpoints: list[GraphCheckpointReference] = []
    for index, raw_reference in enumerate(raw_checkpoints):
        reference = _require_mapping(
            raw_reference,
            context=f"graph checkpoint index.checkpoints[{index}]",
        )
        checkpoints.append(
            GraphCheckpointReference(
                checkpoint_id=_require_string(
                    reference.get("checkpoint_id"),
                    context=f"graph checkpoint index.checkpoints[{index}].checkpoint_id",
                ),
                step_index=_require_int(
                    reference.get("step_index"),
                    context=f"graph checkpoint index.checkpoints[{index}].step_index",
                ),
                time=_require_float(
                    reference.get("time"),
                    context=f"graph checkpoint index.checkpoints[{index}].time",
                ),
                checkpoint_label=_require_string(
                    reference.get("checkpoint_label"),
                    context=f"graph checkpoint index.checkpoints[{index}].checkpoint_label",
                ),
                checkpoint_reason=_optional_string(
                    reference.get("checkpoint_reason"),
                    context=f"graph checkpoint index.checkpoints[{index}].checkpoint_reason",
                ),
                path=_require_string(
                    reference.get("path"),
                    context=f"graph checkpoint index.checkpoints[{index}].path",
                ),
                storage_kind=_require_string(
                    reference.get("storage_kind", "file"),
                    context=f"graph checkpoint index.checkpoints[{index}].storage_kind",
                ),
                chunk_line_index=_optional_int(
                    reference.get("chunk_line_index"),
                    context=f"graph checkpoint index.checkpoints[{index}].chunk_line_index",
                ),
                event_step_range=_require_string_keyed_int_mapping(
                    reference.get("event_step_range", {}),
                    context=f"graph checkpoint index.checkpoints[{index}].event_step_range",
                ),
                event_count_window=_require_int(
                    reference.get("event_count_window", 0),
                    context=f"graph checkpoint index.checkpoints[{index}].event_count_window",
                ),
                event_counts_by_kind_window=_require_string_keyed_int_mapping(
                    reference.get("event_counts_by_kind_window", {}),
                    context=(
                        f"graph checkpoint index.checkpoints[{index}]."
                        "event_counts_by_kind_window"
                    ),
                ),
            )
        )
    return GraphCheckpointIndex(
        identity=_identity_from_json(mapping.get("identity")),
        selection_policy=_require_string(
            mapping.get("selection_policy"),
            context="graph checkpoint index.selection_policy",
        ),
        selection_params=_require_string_keyed_mapping(
            mapping.get("selection_params", {}),
            context="graph checkpoint index.selection_params",
        ),
        checkpoints=tuple(checkpoints),
        family_extensions=_require_family_extensions(
            mapping.get("family_extensions", {}),
            context="graph checkpoint index.family_extensions",
        ),
    )


def save_step_rows(path: str | Path, rows: Sequence[StepTelemetryRow]) -> None:
    """Write step telemetry rows atomically as canonical JSONL."""

    payload = "".join(f"{canonical_json_dumps(_step_row_to_json(row))}\n" for row in rows)
    _atomic_write_text(path, payload)


def load_step_rows(path: str | Path) -> tuple[StepTelemetryRow, ...]:
    """Load step telemetry rows from canonical JSONL."""

    return tuple(
        _step_row_from_json(_decode_json_line(line, context="step telemetry row"))
        for line in _read_jsonl_lines(path)
    )


def save_event_rows(path: str | Path, rows: Sequence[EventTelemetryRow]) -> None:
    """Write event telemetry rows atomically as canonical JSONL."""

    payload = "".join(f"{canonical_json_dumps(_event_row_to_json(row))}\n" for row in rows)
    _atomic_write_text(path, payload)


def load_event_rows(path: str | Path) -> tuple[EventTelemetryRow, ...]:
    """Load event telemetry rows from canonical JSONL."""

    return tuple(
        _event_row_from_json(_decode_json_line(line, context="event telemetry row"))
        for line in _read_jsonl_lines(path)
    )


def save_run_summary(path: str | Path, summary: RunTelemetrySummary) -> None:
    """Write one run summary atomically as canonical JSON."""

    _atomic_write_text(path, canonical_json_dumps(_run_summary_to_json(summary)))


def load_run_summary(path: str | Path) -> RunTelemetrySummary:
    """Load one run summary from canonical JSON."""

    return _run_summary_from_json(_load_json_document(path, context="run telemetry summary"))


def save_comparison_report(path: str | Path, report: TelemetryComparisonReport) -> None:
    """Write one comparison report atomically as canonical JSON."""

    _atomic_write_text(path, canonical_json_dumps(_report_to_json(report)))


def load_comparison_report(path: str | Path) -> TelemetryComparisonReport:
    """Load one comparison report from canonical JSON."""

    return _comparison_report_from_json(
        _load_json_document(path, context="comparison telemetry report")
    )


def save_experiment_report(path: str | Path, report: TelemetryExperimentReport) -> None:
    """Write one experiment report atomically as canonical JSON."""

    _atomic_write_text(path, canonical_json_dumps(_report_to_json(report)))


def load_experiment_report(path: str | Path) -> TelemetryExperimentReport:
    """Load one experiment report from canonical JSON."""

    return _experiment_report_from_json(
        _load_json_document(path, context="experiment telemetry report")
    )


def build_graph_checkpoint_path(
    layout: TelemetryArtifactLayout,
    checkpoint_id: str,
) -> Path:
    """Build the deterministic path for one graph checkpoint payload."""

    if not isinstance(checkpoint_id, str) or not checkpoint_id.strip():
        raise TelemetryArtifactError("checkpoint_id must be a non-empty string")
    return layout.graph_checkpoints_dir / f"{checkpoint_id}.json"


def build_graph_checkpoint_chunk_path(
    layout: TelemetryArtifactLayout,
    chunk_index: int,
) -> Path:
    """Build the deterministic path for one graph checkpoint JSONL chunk."""

    if chunk_index <= 0:
        raise TelemetryArtifactError("chunk_index must be > 0")
    return (
        layout.graph_checkpoints_dir
        / f"{GRAPH_CHECKPOINT_CHUNK_PREFIX}{chunk_index:08d}{GRAPH_CHECKPOINT_CHUNK_SUFFIX}"
    )


def save_graph_checkpoint(path: str | Path, checkpoint: GraphCheckpointArtifact) -> None:
    """Write one graph checkpoint atomically as canonical JSON."""

    _atomic_write_text(path, canonical_json_dumps(_graph_checkpoint_to_json(checkpoint)))


def load_graph_checkpoint(path: str | Path) -> GraphCheckpointArtifact:
    """Load one graph checkpoint from canonical JSON."""

    return _graph_checkpoint_from_json(
        _load_json_document(path, context="graph checkpoint artifact")
    )


def load_graph_checkpoint_from_reference(
    layout: TelemetryArtifactLayout,
    reference: GraphCheckpointReference,
) -> GraphCheckpointArtifact:
    """Load one graph checkpoint from a file or chunk reference."""

    reference_path = layout.graph_checkpoints_dir / reference.path
    if reference.storage_kind == "file":
        return load_graph_checkpoint(reference_path)
    if reference.storage_kind != "jsonl_chunk":
        raise TelemetryArtifactError(
            f"unsupported graph checkpoint storage_kind {reference.storage_kind!r}"
        )
    line_index = reference.chunk_line_index
    if line_index is None:
        raise TelemetryArtifactError("jsonl_chunk graph checkpoint reference is missing chunk_line_index")
    lines = _read_jsonl_lines(reference_path)
    try:
        line = lines[line_index]
    except IndexError as exc:
        raise TelemetryArtifactError(
            f"graph checkpoint reference points past end of chunk file {reference.path!r}"
        ) from exc
    return _graph_checkpoint_from_json(
        _decode_json_line(line, context="graph checkpoint artifact")
    )


def save_graph_checkpoint_index(path: str | Path, index: GraphCheckpointIndex) -> None:
    """Write one graph checkpoint index atomically as canonical JSON."""

    _atomic_write_text(path, canonical_json_dumps(_graph_checkpoint_index_to_json(index)))


def load_graph_checkpoint_index(path: str | Path) -> GraphCheckpointIndex:
    """Load one graph checkpoint index from canonical JSON."""

    return _graph_checkpoint_index_from_json(
        _load_json_document(path, context="graph checkpoint index")
    )


def save_telemetry_artifact_pack(
    layout: TelemetryArtifactLayout,
    *,
    step_rows: Sequence[StepTelemetryRow],
    event_rows: Sequence[EventTelemetryRow],
    run_summary: RunTelemetrySummary,
    graph_checkpoint_index: GraphCheckpointIndex | None = None,
    graph_checkpoints: Sequence[GraphCheckpointArtifact] = (),
) -> None:
    """Write one standard telemetry artifact pack to its run directory."""

    save_step_rows(layout.step_rows_path, step_rows)
    save_event_rows(layout.event_rows_path, event_rows)
    save_run_summary(layout.run_summary_path, run_summary)
    if graph_checkpoint_index is not None:
        save_graph_checkpoint_index(layout.graph_checkpoint_index_path, graph_checkpoint_index)
        for checkpoint in graph_checkpoints:
            save_graph_checkpoint(
                build_graph_checkpoint_path(layout, checkpoint.checkpoint_id),
                checkpoint,
            )


def load_telemetry_artifact_pack(layout: TelemetryArtifactLayout) -> TelemetryArtifactPack:
    """Load one standard telemetry artifact pack from its run directory."""
    graph_checkpoint_index = (
        None
        if not layout.graph_checkpoint_index_path.exists()
        else load_graph_checkpoint_index(layout.graph_checkpoint_index_path)
    )
    graph_checkpoints: tuple[GraphCheckpointArtifact, ...] = ()
    if graph_checkpoint_index is not None:
        graph_checkpoints = tuple(
            load_graph_checkpoint_from_reference(layout, reference)
            for reference in graph_checkpoint_index.checkpoints
        )
    return TelemetryArtifactPack(
        layout=layout,
        step_rows=load_step_rows(layout.step_rows_path),
        event_rows=load_event_rows(layout.event_rows_path),
        run_summary=load_run_summary(layout.run_summary_path),
        experiment_report=(
            None
            if not layout.experiment_report_path.exists()
            else load_experiment_report(layout.experiment_report_path)
        ),
        comparison_report=(
            None
            if not layout.comparison_report_path.exists()
            else load_comparison_report(layout.comparison_report_path)
        ),
        graph_checkpoint_index=graph_checkpoint_index,
        graph_checkpoints=graph_checkpoints,
    )


def _read_jsonl_lines(path: str | Path) -> tuple[str, ...]:
    text = Path(path).read_text(encoding="utf-8")
    if not text:
        return ()
    return tuple(line for line in text.splitlines() if line.strip())


def _decode_json_line(line: str, *, context: str) -> Any:
    try:
        decoded = json.loads(line)
    except json.JSONDecodeError as exc:
        raise TelemetryArtifactError(f"invalid {context} JSON: {exc}") from exc
    return decoded


def _load_json_document(path: str | Path, *, context: str) -> Any:
    payload = Path(path).read_text(encoding="utf-8")
    try:
        decoded = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise TelemetryArtifactError(f"invalid {context} JSON: {exc}") from exc
    return decoded


def _require_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TelemetryArtifactError(f"{context} must be a mapping")
    return value


def _require_string_keyed_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    mapping = _require_mapping(value, context=context)
    non_string_keys = [key for key in mapping if not isinstance(key, str)]
    if non_string_keys:
        raise TelemetryArtifactError(
            f"{context} must use string keys; got non-string keys {non_string_keys!r}"
        )
    return canonicalize_json_value(mapping)


def _require_record_sequence(value: Any, *, context: str) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise TelemetryArtifactError(f"{context} must be a sequence of mappings")
    records: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        records.append(
            _require_string_keyed_mapping(
                item,
                context=f"{context}[{index}]",
            )
        )
    return tuple(records)


def _require_family_extensions(value: Any, *, context: str) -> Mapping[str, Mapping[str, Any]]:
    mapping = _require_string_keyed_mapping(value, context=context)
    result: dict[str, Mapping[str, Any]] = {}
    for family_name, payload in mapping.items():
        result[family_name] = _require_string_keyed_mapping(
            payload,
            context=f"{context}[{family_name}]",
        )
    return result


def _require_string_keyed_int_mapping(value: Any, *, context: str) -> Mapping[str, int]:
    mapping = _require_string_keyed_mapping(value, context=context)
    result: dict[str, int] = {}
    for key, item in mapping.items():
        result[key] = _require_int(item, context=f"{context}[{key}]")
    return result


def _require_string(value: Any, *, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise TelemetryArtifactError(f"{context} must be a non-empty string")
    return value


def _optional_string(value: Any, *, context: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, context=context)


def _require_int(value: Any, *, context: str) -> int:
    if not isinstance(value, int):
        raise TelemetryArtifactError(f"{context} must be an int")
    return value


def _optional_int(value: Any, *, context: str) -> int | None:
    if value is None:
        return None
    return _require_int(value, context=context)


def _require_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TelemetryArtifactError(f"{context} must be a float-compatible number")
    return float(value)


__all__ = [
    "COMPARISON_REPORT_FILENAME",
    "DEFAULT_EXPERIMENTS_ROOT",
    "DEFAULT_OUTPUTS_ROOT",
    "DEFAULT_TELEMETRY_ROOT",
    "EVENT_ROWS_FILENAME",
    "EXPERIMENT_REPORT_FILENAME",
    "GRAPH_CHECKPOINT_CHUNK_PREFIX",
    "GRAPH_CHECKPOINT_CHUNK_SUFFIX",
    "GRAPH_CHECKPOINT_INDEX_FILENAME",
    "GRAPH_CHECKPOINTS_DIRNAME",
    "RUN_SUMMARY_FILENAME",
    "STEP_ROWS_FILENAME",
    "TELEMETRY_DIRNAME",
    "GraphCheckpointChunkWriter",
    "TelemetryArtifactError",
    "TelemetryArtifactLayout",
    "TelemetryArtifactPack",
    "build_graph_checkpoint_chunk_path",
    "build_graph_checkpoint_path",
    "build_telemetry_artifact_layout",
    "load_graph_checkpoint",
    "load_graph_checkpoint_from_reference",
    "load_graph_checkpoint_index",
    "load_comparison_report",
    "load_event_rows",
    "load_experiment_report",
    "load_run_summary",
    "load_step_rows",
    "load_telemetry_artifact_pack",
    "resolve_telemetry_root",
    "save_graph_checkpoint",
    "save_graph_checkpoint_index",
    "save_comparison_report",
    "save_event_rows",
    "save_experiment_report",
    "save_run_summary",
    "save_step_rows",
    "save_telemetry_artifact_pack",
]
