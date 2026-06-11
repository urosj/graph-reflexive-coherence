"""Shared telemetry schema types and builders for PyGRC experiment artifacts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, TypeAlias

from pygrc.core import GRCEvent, StepResult, digest_canonical_data


STEP_TELEMETRY_KIND = "step"
EVENT_TELEMETRY_KIND = "event"
RUN_SUMMARY_KIND = "run_summary"
COMPARISON_REPORT_KIND = "comparison_report"
EXPERIMENT_REPORT_KIND = "experiment_report"
GRAPH_CHECKPOINT_KIND = "graph_checkpoint"
GRAPH_CHECKPOINT_INDEX_KIND = "graph_checkpoint_index"

TELEMETRY_RECORD_KINDS: tuple[str, ...] = (
    STEP_TELEMETRY_KIND,
    EVENT_TELEMETRY_KIND,
    RUN_SUMMARY_KIND,
    COMPARISON_REPORT_KIND,
    EXPERIMENT_REPORT_KIND,
)

TelemetryCommonFields: TypeAlias = Mapping[str, Any]
TelemetryFamilyExtensions: TypeAlias = Mapping[str, Mapping[str, Any]]
EventCountsByKind: TypeAlias = Mapping[str, int]


def _freeze_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key in sorted(value):
            frozen[key] = _freeze_value(value[key])
        return MappingProxyType(frozen)
    if isinstance(value, list | tuple):
        return tuple(_freeze_value(item) for item in value)
    return value


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return _freeze_value(value)


def _freeze_extensions(value: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Mapping[str, Any]]:
    frozen: dict[str, Mapping[str, Any]] = {}
    for family_name in sorted(value):
        frozen[family_name] = _freeze_mapping(value[family_name])
    return MappingProxyType(frozen)


def _freeze_mapping_sequence(values: Sequence[Mapping[str, Any]]) -> tuple[Mapping[str, Any], ...]:
    return tuple(_freeze_mapping(value) for value in values)


def _stringify_mapping_keys(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _stringify_mapping_keys(inner_value)
            for key, inner_value in value.items()
        }
    if isinstance(value, list | tuple):
        return [_stringify_mapping_keys(item) for item in value]
    return value


def _count_events_by_kind(events: Sequence[GRCEvent]) -> Mapping[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        counts[event.kind] = counts.get(event.kind, 0) + 1
    return MappingProxyType(dict(sorted(counts.items())))


def build_run_id(
    *,
    model_family: str,
    params_identity: str | None,
    seed_name: str | None,
    seed_source_reference: str | None,
    seed_path: str | None,
    param_family: str | None,
    rng_seed: int | None,
    requested_steps: int | None,
    overrides: Mapping[str, Any] | None = None,
) -> str:
    """Build one deterministic run identity from replay-critical inputs."""

    return digest_canonical_data(
        {
            "model_family": model_family,
            "params_identity": params_identity,
            "seed_name": seed_name,
            "seed_source_reference": seed_source_reference,
            "seed_path": seed_path,
            "param_family": param_family,
            "rng_seed": rng_seed,
            "requested_steps": requested_steps,
            "overrides": {} if overrides is None else dict(overrides),
        }
    )


@dataclass(frozen=True, kw_only=True)
class RunTelemetryIdentity:
    """Replay-critical run identity and provenance fields shared across telemetry."""

    run_id: str
    model_family: str
    params_identity: str | None
    seed_name: str | None = None
    seed_source_reference: str | None = None
    seed_path: str | None = None
    param_family: str | None = None
    rng_seed: int | None = None
    requested_steps: int | None = None


@dataclass(frozen=True, kw_only=True)
class TelemetryRecord:
    """Generic telemetry payload shared by all later record families."""

    kind: str
    family: str
    common: TelemetryCommonFields
    extensions: TelemetryFamilyExtensions = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if self.kind not in TELEMETRY_RECORD_KINDS:
            raise ValueError(
                f"telemetry record kind must be one of {TELEMETRY_RECORD_KINDS}; "
                f"got {self.kind!r}"
            )
        object.__setattr__(self, "common", _freeze_mapping(self.common))
        object.__setattr__(self, "extensions", _freeze_extensions(self.extensions))


@dataclass(frozen=True, kw_only=True)
class StepTelemetryRow:
    """Canonical per-step telemetry row."""

    identity: RunTelemetryIdentity
    step_index: int
    time: float
    event_count: int
    event_counts_by_kind: EventCountsByKind
    observables: Mapping[str, Any]
    bookkeeping: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    family_extensions: TelemetryFamilyExtensions = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_counts_by_kind", _freeze_mapping(self.event_counts_by_kind))
        object.__setattr__(self, "observables", _freeze_mapping(self.observables))
        object.__setattr__(self, "bookkeeping", _freeze_mapping(self.bookkeeping))
        object.__setattr__(self, "family_extensions", _freeze_extensions(self.family_extensions))

    def to_record(self) -> TelemetryRecord:
        return TelemetryRecord(
            kind=STEP_TELEMETRY_KIND,
            family=self.identity.model_family,
            common={
                "run_id": self.identity.run_id,
                "model_family": self.identity.model_family,
                "params_identity": self.identity.params_identity,
                "seed_name": self.identity.seed_name,
                "seed_source_reference": self.identity.seed_source_reference,
                "seed_path": self.identity.seed_path,
                "param_family": self.identity.param_family,
                "rng_seed": self.identity.rng_seed,
                "requested_steps": self.identity.requested_steps,
                "step_index": self.step_index,
                "time": self.time,
                "event_count": self.event_count,
                "event_counts_by_kind": self.event_counts_by_kind,
                "observables": self.observables,
                "bookkeeping": self.bookkeeping,
            },
            extensions=self.family_extensions,
        )


@dataclass(frozen=True, kw_only=True)
class EventTelemetryRow:
    """Canonical per-event telemetry row."""

    identity: RunTelemetryIdentity
    step_index: int
    event_index: int
    event_kind: str
    source_family: str | None
    payload: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    family_extensions: TelemetryFamilyExtensions = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", _freeze_mapping(self.payload))
        object.__setattr__(self, "family_extensions", _freeze_extensions(self.family_extensions))

    def to_record(self) -> TelemetryRecord:
        return TelemetryRecord(
            kind=EVENT_TELEMETRY_KIND,
            family=self.identity.model_family,
            common={
                "run_id": self.identity.run_id,
                "model_family": self.identity.model_family,
                "params_identity": self.identity.params_identity,
                "seed_name": self.identity.seed_name,
                "seed_source_reference": self.identity.seed_source_reference,
                "seed_path": self.identity.seed_path,
                "param_family": self.identity.param_family,
                "rng_seed": self.identity.rng_seed,
                "requested_steps": self.identity.requested_steps,
                "step_index": self.step_index,
                "event_index": self.event_index,
                "event_kind": self.event_kind,
                "source_family": self.source_family,
                "payload": self.payload,
            },
            extensions=self.family_extensions,
        )


@dataclass(frozen=True, kw_only=True)
class RunTelemetrySummary:
    """Canonical run-summary payload derived from one full trajectory."""

    identity: RunTelemetryIdentity
    completed_steps: int
    final_step_index: int
    initial_time: float
    final_time: float
    total_event_count: int
    event_counts_by_kind: EventCountsByKind
    initial_observables: Mapping[str, Any]
    final_observables: Mapping[str, Any]
    resolved_params: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    raw_params: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    parameter_overrides: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    status: str = "completed"
    family_extensions: TelemetryFamilyExtensions = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_counts_by_kind", _freeze_mapping(self.event_counts_by_kind))
        object.__setattr__(self, "initial_observables", _freeze_mapping(self.initial_observables))
        object.__setattr__(self, "final_observables", _freeze_mapping(self.final_observables))
        object.__setattr__(self, "resolved_params", _freeze_mapping(self.resolved_params))
        object.__setattr__(self, "raw_params", _freeze_mapping(self.raw_params))
        object.__setattr__(self, "parameter_overrides", _freeze_mapping(self.parameter_overrides))
        object.__setattr__(self, "family_extensions", _freeze_extensions(self.family_extensions))

    def to_record(self) -> TelemetryRecord:
        return TelemetryRecord(
            kind=RUN_SUMMARY_KIND,
            family=self.identity.model_family,
            common={
                "run_id": self.identity.run_id,
                "model_family": self.identity.model_family,
                "params_identity": self.identity.params_identity,
                "seed_name": self.identity.seed_name,
                "seed_source_reference": self.identity.seed_source_reference,
                "seed_path": self.identity.seed_path,
                "param_family": self.identity.param_family,
                "rng_seed": self.identity.rng_seed,
                "requested_steps": self.identity.requested_steps,
                "completed_steps": self.completed_steps,
                "final_step_index": self.final_step_index,
                "initial_time": self.initial_time,
                "final_time": self.final_time,
                "total_event_count": self.total_event_count,
                "event_counts_by_kind": self.event_counts_by_kind,
                "initial_observables": self.initial_observables,
                "final_observables": self.final_observables,
                "resolved_params": self.resolved_params,
                "raw_params": self.raw_params,
                "parameter_overrides": self.parameter_overrides,
                "status": self.status,
            },
            extensions=self.family_extensions,
        )


@dataclass(frozen=True, kw_only=True)
class TelemetryComparisonReport(TelemetryRecord):
    """Shared comparison-report telemetry envelope."""

    kind: str = COMPARISON_REPORT_KIND


@dataclass(frozen=True, kw_only=True)
class TelemetryExperimentReport(TelemetryRecord):
    """Shared experiment-report telemetry envelope."""

    kind: str = EXPERIMENT_REPORT_KIND


@dataclass(frozen=True, kw_only=True)
class GraphCheckpointArtifact:
    """Saved graph-checkpoint payload for graph-visible telemetry."""

    identity: RunTelemetryIdentity
    checkpoint_id: str
    step_index: int
    time: float
    checkpoint_label: str
    graph_kind: str
    node_count: int
    edge_count: int
    node_records: tuple[Mapping[str, Any], ...]
    edge_records: tuple[Mapping[str, Any], ...]
    checkpoint_reason: str | None = None
    event_step_range: Mapping[str, int] = field(default_factory=lambda: MappingProxyType({}))
    event_count_window: int = 0
    event_counts_by_kind_window: EventCountsByKind = field(
        default_factory=lambda: MappingProxyType({})
    )
    flow_representation: str | None = None
    flow_cadence: str | None = None
    layout_mode: str | None = None
    layout_dimensions: int | None = None
    layout_hints: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    label_computation_modes: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )
    topology_extensions: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )
    family_extensions: TelemetryFamilyExtensions = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "node_records", _freeze_mapping_sequence(self.node_records))
        object.__setattr__(self, "edge_records", _freeze_mapping_sequence(self.edge_records))
        object.__setattr__(self, "event_step_range", _freeze_mapping(self.event_step_range))
        object.__setattr__(
            self,
            "event_counts_by_kind_window",
            _freeze_mapping(self.event_counts_by_kind_window),
        )
        object.__setattr__(self, "layout_hints", _freeze_mapping(self.layout_hints))
        object.__setattr__(
            self,
            "label_computation_modes",
            _freeze_mapping(self.label_computation_modes),
        )
        object.__setattr__(
            self,
            "topology_extensions",
            _freeze_mapping(self.topology_extensions),
        )
        object.__setattr__(self, "family_extensions", _freeze_extensions(self.family_extensions))


@dataclass(frozen=True, kw_only=True)
class GraphCheckpointReference:
    """Index entry for one saved graph checkpoint."""

    checkpoint_id: str
    step_index: int
    time: float
    checkpoint_label: str
    path: str
    storage_kind: str = "file"
    chunk_line_index: int | None = None
    checkpoint_reason: str | None = None
    event_step_range: Mapping[str, int] = field(default_factory=lambda: MappingProxyType({}))
    event_count_window: int = 0
    event_counts_by_kind_window: EventCountsByKind = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        if self.storage_kind not in {"file", "jsonl_chunk"}:
            raise ValueError(
                "graph checkpoint reference storage_kind must be 'file' or 'jsonl_chunk'"
            )
        if self.storage_kind == "file" and self.chunk_line_index is not None:
            raise ValueError("file-backed graph checkpoint references must not set chunk_line_index")
        if self.storage_kind == "jsonl_chunk":
            if self.chunk_line_index is None or self.chunk_line_index < 0:
                raise ValueError(
                    "jsonl_chunk graph checkpoint references must set a non-negative "
                    "chunk_line_index"
                )
        object.__setattr__(self, "event_step_range", _freeze_mapping(self.event_step_range))
        object.__setattr__(
            self,
            "event_counts_by_kind_window",
            _freeze_mapping(self.event_counts_by_kind_window),
        )


@dataclass(frozen=True, kw_only=True)
class GraphCheckpointIndex:
    """Deterministic checkpoint index for one run's graph-visible artifacts."""

    identity: RunTelemetryIdentity
    selection_policy: str
    selection_params: Mapping[str, Any]
    checkpoints: tuple[GraphCheckpointReference, ...]
    family_extensions: TelemetryFamilyExtensions = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "selection_params", _freeze_mapping(self.selection_params))
        object.__setattr__(self, "family_extensions", _freeze_extensions(self.family_extensions))


def step_row_from_step_result(
    step_result: StepResult,
    *,
    identity: RunTelemetryIdentity,
    family_extensions: Mapping[str, Mapping[str, Any]] | None = None,
) -> StepTelemetryRow:
    """Build one canonical step row from the shared runtime step result."""

    return StepTelemetryRow(
        identity=identity,
        step_index=step_result.step_index,
        time=float(step_result.time),
        event_count=len(step_result.events),
        event_counts_by_kind=_count_events_by_kind(step_result.events),
        observables=dict(_stringify_mapping_keys(dict(step_result.observables))),
        bookkeeping=dict(_stringify_mapping_keys(dict(step_result.bookkeeping))),
        family_extensions={} if family_extensions is None else family_extensions,
    )


def event_rows_from_events(
    events: Sequence[GRCEvent],
    *,
    identity: RunTelemetryIdentity,
    family_extensions: Mapping[str, Mapping[str, Any]] | None = None,
    family_extensions_by_event: Sequence[Mapping[str, Mapping[str, Any]]] | None = None,
) -> tuple[EventTelemetryRow, ...]:
    """Build canonical event rows from one ordered event sequence."""

    shared_extensions = {} if family_extensions is None else family_extensions
    if family_extensions_by_event is not None and len(family_extensions_by_event) != len(events):
        raise ValueError("family_extensions_by_event must match the events length")
    return tuple(
        EventTelemetryRow(
            identity=identity,
            step_index=event.step_index,
            event_index=index,
            event_kind=event.kind,
            source_family=event.source_family,
            payload=dict(event.payload),
            family_extensions=(
                shared_extensions
                if family_extensions_by_event is None
                else family_extensions_by_event[index]
            ),
        )
        for index, event in enumerate(events)
    )


def run_summary_from_step_results(
    step_results: Sequence[StepResult],
    *,
    identity: RunTelemetryIdentity,
    initial_observables: Mapping[str, Any],
    final_observables: Mapping[str, Any],
    resolved_params: Mapping[str, Any] | None = None,
    raw_params: Mapping[str, Any] | None = None,
    parameter_overrides: Mapping[str, Any] | None = None,
    family_extensions: Mapping[str, Mapping[str, Any]] | None = None,
) -> RunTelemetrySummary:
    """Build one canonical run summary from an ordered step-result trajectory."""

    all_events: list[GRCEvent] = []
    for step_result in step_results:
        all_events.extend(step_result.events)

    initial_time = 0.0
    if step_results:
        final_time = float(step_results[-1].time)
        final_step_index = int(step_results[-1].step_index)
    else:
        final_time = 0.0
        final_step_index = 0

    return RunTelemetrySummary(
        identity=identity,
        completed_steps=len(step_results),
        final_step_index=final_step_index,
        initial_time=initial_time,
        final_time=final_time,
        total_event_count=len(all_events),
        event_counts_by_kind=_count_events_by_kind(all_events),
        initial_observables=dict(_stringify_mapping_keys(dict(initial_observables))),
        final_observables=dict(_stringify_mapping_keys(dict(final_observables))),
        resolved_params={} if resolved_params is None else dict(resolved_params),
        raw_params={} if raw_params is None else dict(raw_params),
        parameter_overrides={} if parameter_overrides is None else dict(parameter_overrides),
        family_extensions={} if family_extensions is None else family_extensions,
    )


__all__ = [
    "COMPARISON_REPORT_KIND",
    "EVENT_TELEMETRY_KIND",
    "EXPERIMENT_REPORT_KIND",
    "GRAPH_CHECKPOINT_INDEX_KIND",
    "GRAPH_CHECKPOINT_KIND",
    "RUN_SUMMARY_KIND",
    "STEP_TELEMETRY_KIND",
    "TELEMETRY_RECORD_KINDS",
    "EventCountsByKind",
    "EventTelemetryRow",
    "GraphCheckpointArtifact",
    "GraphCheckpointIndex",
    "GraphCheckpointReference",
    "RunTelemetryIdentity",
    "RunTelemetrySummary",
    "StepTelemetryRow",
    "TelemetryCommonFields",
    "TelemetryComparisonReport",
    "TelemetryExperimentReport",
    "TelemetryFamilyExtensions",
    "TelemetryRecord",
    "build_run_id",
    "event_rows_from_events",
    "run_summary_from_step_results",
    "step_row_from_step_result",
]
