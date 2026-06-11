"""Runner-level telemetry recording helpers for executable PyGRC runs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

from pygrc.core import StepResult

from .io import (
    DEFAULT_TELEMETRY_ROOT,
    TelemetryArtifactLayout,
    build_telemetry_artifact_layout,
    save_telemetry_artifact_pack,
)
from .schema import (
    EventTelemetryRow,
    GraphCheckpointArtifact,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    RunTelemetrySummary,
    StepTelemetryRow,
    build_run_id,
    event_rows_from_events,
    run_summary_from_step_results,
    step_row_from_step_result,
)


TelemetryFamilyExtensionMapping: TypeAlias = Mapping[str, Mapping[str, Any]]


@dataclass(frozen=True, kw_only=True)
class GraphCheckpointCaptureConfig:
    """Configuration for checkpoint graph/flow artifact capture."""

    include_initial: bool = True
    include_final: bool = True
    every_step: bool = False
    every_n_steps: int | None = None
    include_flow_overlays: bool = False
    storage_mode: str = "per_checkpoint_files"
    chunk_size: int = 100

    def __post_init__(self) -> None:
        if self.every_step and self.every_n_steps is not None:
            raise ValueError("every_step and every_n_steps are mutually exclusive")
        if self.every_n_steps is not None and self.every_n_steps <= 0:
            raise ValueError("every_n_steps must be > 0 when provided")
        if self.storage_mode not in {"per_checkpoint_files", "jsonl_chunks"}:
            raise ValueError(
                "storage_mode must be 'per_checkpoint_files' or 'jsonl_chunks'"
            )
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")

    @property
    def selection_policy(self) -> str:
        parts: list[str] = []
        if self.include_initial:
            parts.append("initial")
        if self.include_final:
            parts.append("final")
        if self.every_step:
            parts.append("every_step")
        elif self.every_n_steps is not None:
            parts.append("every_n_steps")
        return "+".join(parts) if parts else "none"

    @property
    def selection_params(self) -> Mapping[str, Any]:
        params: dict[str, Any] = {
            "include_initial": self.include_initial,
            "include_final": self.include_final,
            "include_flow_overlays": self.include_flow_overlays,
            "storage_mode": self.storage_mode,
        }
        if self.every_step:
            params["every_step"] = True
        elif self.every_n_steps is not None:
            params["every_n_steps"] = self.every_n_steps
        if self.storage_mode == "jsonl_chunks":
            params["chunk_size"] = self.chunk_size
        return params


@dataclass(frozen=True, kw_only=True)
class TelemetryCaptureConfig:
    """Configuration for runtime telemetry capture at the runner boundary."""

    root_dir: str | Path = DEFAULT_TELEMETRY_ROOT
    experiment_path: str | Path | None = None
    write_artifacts: bool = False
    graph_checkpoints: GraphCheckpointCaptureConfig | None = None


@dataclass(frozen=True)
class TelemetryCaptureResult:
    """In-memory telemetry capture plus optional artifact layout."""

    identity: RunTelemetryIdentity
    step_rows: tuple[StepTelemetryRow, ...]
    event_rows: tuple[EventTelemetryRow, ...]
    run_summary: RunTelemetrySummary
    artifact_layout: TelemetryArtifactLayout | None = None
    graph_checkpoint_index: GraphCheckpointIndex | None = None
    graph_checkpoints: tuple[GraphCheckpointArtifact, ...] = ()


def capture_run_telemetry(
    *,
    model_family: str,
    params_identity: str | None,
    seed_name: str | None,
    seed_source_reference: str | None,
    seed_path: str | None,
    param_family: str | None,
    rng_seed: int | None,
    requested_steps: int | None,
    initial_observables: Mapping[str, Any],
    step_results: Sequence[StepResult],
    final_observables: Mapping[str, Any],
    resolved_params: Mapping[str, Any] | None = None,
    raw_params: Mapping[str, Any] | None = None,
    overrides: Mapping[str, Any] | None = None,
    family_extensions: TelemetryFamilyExtensionMapping | None = None,
    step_family_extensions: Sequence[TelemetryFamilyExtensionMapping] | None = None,
    event_family_extensions_by_step: Sequence[
        Sequence[TelemetryFamilyExtensionMapping]
    ] | None = None,
    summary_family_extensions: TelemetryFamilyExtensionMapping | None = None,
    graph_checkpoints: Sequence[GraphCheckpointArtifact] | None = None,
    graph_checkpoint_index: GraphCheckpointIndex | None = None,
    artifact_layout: TelemetryArtifactLayout | None = None,
    config: TelemetryCaptureConfig | None = None,
) -> TelemetryCaptureResult:
    """Capture one executable run into shared telemetry rows and summary."""

    run_id = build_run_id(
        model_family=model_family,
        params_identity=params_identity,
        seed_name=seed_name,
        seed_source_reference=seed_source_reference,
        seed_path=seed_path,
        param_family=param_family,
        rng_seed=rng_seed,
        requested_steps=requested_steps,
        overrides=overrides,
    )
    identity = RunTelemetryIdentity(
        run_id=run_id,
        model_family=model_family,
        params_identity=params_identity,
        seed_name=seed_name,
        seed_source_reference=seed_source_reference,
        seed_path=seed_path,
        param_family=param_family,
        rng_seed=rng_seed,
        requested_steps=requested_steps,
    )
    shared_extensions: TelemetryFamilyExtensionMapping = (
        {} if family_extensions is None else family_extensions
    )
    resolved_step_extensions = _resolve_step_family_extensions(
        step_results=step_results,
        step_family_extensions=step_family_extensions,
    )
    resolved_event_extensions = _resolve_event_family_extensions(
        step_results=step_results,
        event_family_extensions_by_step=event_family_extensions_by_step,
    )
    step_rows = tuple(
        step_row_from_step_result(
            step_result,
            identity=identity,
            family_extensions=_merge_family_extensions(
                shared_extensions,
                resolved_step_extensions[index],
            ),
        )
        for index, step_result in enumerate(step_results)
    )

    event_rows_list: list[EventTelemetryRow] = []
    for step_index, step_result in enumerate(step_results):
        event_rows_list.extend(
            event_rows_from_events(
                step_result.events,
                identity=identity,
                family_extensions_by_event=[
                    _merge_family_extensions(shared_extensions, event_extensions)
                    for event_extensions in resolved_event_extensions[step_index]
                ],
            )
        )

    run_summary = run_summary_from_step_results(
        step_results,
        identity=identity,
        initial_observables=initial_observables,
        final_observables=final_observables,
        resolved_params=resolved_params,
        raw_params=raw_params,
        parameter_overrides=overrides,
        family_extensions=_merge_family_extensions(
            shared_extensions,
            {} if summary_family_extensions is None else summary_family_extensions,
        ),
    )

    resolved_config = config if config is not None else TelemetryCaptureConfig()
    graph_checkpoint_tuple = tuple(graph_checkpoints or ())
    resolved_graph_checkpoint_index = graph_checkpoint_index
    if resolved_graph_checkpoint_index is None:
        resolved_graph_checkpoint_index = _build_graph_checkpoint_index(
            identity=identity,
            graph_checkpoints=graph_checkpoint_tuple,
            config=resolved_config.graph_checkpoints,
        )
    resolved_artifact_layout: TelemetryArtifactLayout | None = None
    if resolved_config.write_artifacts:
        resolved_artifact_layout = (
            artifact_layout
            if artifact_layout is not None
            else build_telemetry_artifact_layout(
                run_id,
                root_dir=resolved_config.root_dir,
                experiment_path=resolved_config.experiment_path,
            )
        )
        save_telemetry_artifact_pack(
            resolved_artifact_layout,
            step_rows=step_rows,
            event_rows=event_rows_list,
            run_summary=run_summary,
            graph_checkpoint_index=resolved_graph_checkpoint_index,
            graph_checkpoints=graph_checkpoint_tuple,
        )

    return TelemetryCaptureResult(
        identity=identity,
        step_rows=step_rows,
        event_rows=tuple(event_rows_list),
        run_summary=run_summary,
        artifact_layout=resolved_artifact_layout,
        graph_checkpoint_index=resolved_graph_checkpoint_index,
        graph_checkpoints=graph_checkpoint_tuple,
    )


def _build_graph_checkpoint_index(
    *,
    identity: RunTelemetryIdentity,
    graph_checkpoints: Sequence[GraphCheckpointArtifact],
    config: GraphCheckpointCaptureConfig | None,
) -> GraphCheckpointIndex | None:
    if not graph_checkpoints:
        return None
    selection_policy = "explicit"
    selection_params: Mapping[str, Any] = {}
    if config is not None:
        selection_policy = config.selection_policy
        selection_params = config.selection_params
    return GraphCheckpointIndex(
        identity=identity,
        selection_policy=selection_policy,
        selection_params=selection_params,
        checkpoints=tuple(
            GraphCheckpointReference(
                checkpoint_id=checkpoint.checkpoint_id,
                step_index=checkpoint.step_index,
                time=checkpoint.time,
                checkpoint_label=checkpoint.checkpoint_label,
                checkpoint_reason=checkpoint.checkpoint_reason,
                path=f"{checkpoint.checkpoint_id}.json",
                event_step_range=checkpoint.event_step_range,
                event_count_window=checkpoint.event_count_window,
                event_counts_by_kind_window=checkpoint.event_counts_by_kind_window,
            )
            for checkpoint in graph_checkpoints
        ),
    )


def _merge_family_extensions(
    base: TelemetryFamilyExtensionMapping,
    override: TelemetryFamilyExtensionMapping,
) -> TelemetryFamilyExtensionMapping:
    if not base:
        return dict(override)
    if not override:
        return dict(base)
    merged: dict[str, dict[str, Any]] = {
        family_name: dict(payload)
        for family_name, payload in base.items()
    }
    for family_name, payload in override.items():
        family_payload = merged.setdefault(family_name, {})
        family_payload.update(dict(payload))
    return merged


def _resolve_step_family_extensions(
    *,
    step_results: Sequence[StepResult],
    step_family_extensions: Sequence[TelemetryFamilyExtensionMapping] | None,
) -> tuple[TelemetryFamilyExtensionMapping, ...]:
    if step_family_extensions is None:
        return tuple({} for _ in step_results)
    if len(step_family_extensions) != len(step_results):
        raise ValueError("step_family_extensions must match the step_results length")
    return tuple(dict(extensions) for extensions in step_family_extensions)


def _resolve_event_family_extensions(
    *,
    step_results: Sequence[StepResult],
    event_family_extensions_by_step: Sequence[Sequence[TelemetryFamilyExtensionMapping]] | None,
) -> tuple[tuple[TelemetryFamilyExtensionMapping, ...], ...]:
    if event_family_extensions_by_step is None:
        return tuple(tuple({} for _ in step_result.events) for step_result in step_results)
    if len(event_family_extensions_by_step) != len(step_results):
        raise ValueError(
            "event_family_extensions_by_step must match the step_results length"
        )
    resolved: list[tuple[TelemetryFamilyExtensionMapping, ...]] = []
    for step_result, per_step_extensions in zip(step_results, event_family_extensions_by_step):
        if len(per_step_extensions) != len(step_result.events):
            raise ValueError(
                "each event_family_extensions_by_step entry must match the number of "
                "events in the corresponding step result"
            )
        resolved.append(tuple(dict(extensions) for extensions in per_step_extensions))
    return tuple(resolved)


__all__ = [
    "GraphCheckpointCaptureConfig",
    "TelemetryCaptureConfig",
    "TelemetryCaptureResult",
    "capture_run_telemetry",
]
