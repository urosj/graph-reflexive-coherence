"""Shared internal lane-runner helpers for GRCV3 telemetry experiments."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pygrc.core import StepResult
from pygrc.models import GRCV3
from pygrc.models.grc_v3_checkpoints import export_grcv3_graph_checkpoint

from .grcv3_contract import (
    classify_grcv3_event_extension,
    grcv3_event_family_extensions,
)
from .io import (
    DEFAULT_TELEMETRY_ROOT,
    GraphCheckpointChunkWriter,
    TelemetryArtifactLayout,
    build_telemetry_artifact_layout,
)
from .recorder import GraphCheckpointCaptureConfig
from .schema import GraphCheckpointIndex, GraphCheckpointReference, RunTelemetryIdentity


@dataclass(frozen=True)
class GRCV3CheckpointConfig:
    """Internal checkpoint config for shared representative/landscape runners."""

    record_graph_checkpoints: bool
    checkpoint_every_step: bool = False
    checkpoint_every_n_steps: int | None = None
    checkpoint_storage_mode: str | None = None
    checkpoint_chunk_size: int = 100
    include_flow_overlays: bool = False

    def __post_init__(self) -> None:
        if not self.record_graph_checkpoints:
            return
        if self.checkpoint_storage_mode is None:
            object.__setattr__(
                self,
                "checkpoint_storage_mode",
                "jsonl_chunks" if self.checkpoint_every_step else "per_checkpoint_files",
            )

    def build_capture_config(self) -> GraphCheckpointCaptureConfig | None:
        if not self.record_graph_checkpoints:
            return None
        return GraphCheckpointCaptureConfig(
            include_initial=True,
            include_final=True,
            every_step=self.checkpoint_every_step,
            every_n_steps=self.checkpoint_every_n_steps,
            include_flow_overlays=self.include_flow_overlays,
            storage_mode=self.checkpoint_storage_mode,
            chunk_size=self.checkpoint_chunk_size,
        )


@dataclass
class GRCV3LaneRunArtifacts:
    """Collected artifacts from a shared internal GRCV3 lane execution."""

    model: GRCV3
    initial_observables: dict[str, Any]
    step_results: list[StepResult]
    final_observables: dict[str, Any]
    step_family_extensions: list[dict[str, dict[str, Any]]]
    event_family_extensions_by_step: list[list[dict[str, dict[str, Any]]]]
    graph_checkpoints: list[Any]
    graph_checkpoint_index: GraphCheckpointIndex | None
    artifact_layout: TelemetryArtifactLayout | None
    graph_checkpoint_capture_config: GraphCheckpointCaptureConfig | None
    initial_context: Any = None


def run_grcv3_lane_with_telemetry(
    *,
    model: GRCV3,
    telemetry_root: str | Path,
    telemetry_experiment_path: str | Path,
    run_identity: RunTelemetryIdentity,
    num_steps: int,
    checkpoint_config: GRCV3CheckpointConfig,
    build_step_family_extension: Callable[[GRCV3], dict[str, dict[str, Any]]],
    pre_step_setup: Callable[[GRCV3], None] | None = None,
    initialize_context: Callable[[GRCV3], Any] | None = None,
) -> GRCV3LaneRunArtifacts:
    """Execute one internal GRCV3 lane with shared checkpoint/extension logic."""

    graph_checkpoint_capture_config = checkpoint_config.build_capture_config()
    streamed_artifact_layout: TelemetryArtifactLayout | None = None
    checkpoint_chunk_writer: GraphCheckpointChunkWriter | None = None
    streamed_checkpoint_references: list[GraphCheckpointReference] = []
    graph_checkpoints: list[Any] = []
    if (
        graph_checkpoint_capture_config is not None
        and graph_checkpoint_capture_config.storage_mode == "jsonl_chunks"
    ):
        streamed_artifact_layout = build_telemetry_artifact_layout(
            run_identity.run_id,
            root_dir=DEFAULT_TELEMETRY_ROOT if telemetry_root is None else telemetry_root,
            experiment_path=telemetry_experiment_path,
        )
        checkpoint_chunk_writer = GraphCheckpointChunkWriter(
            streamed_artifact_layout,
            chunk_size=graph_checkpoint_capture_config.chunk_size,
        )

    def record_graph_checkpoint(checkpoint: Any) -> None:
        if checkpoint_chunk_writer is not None:
            streamed_checkpoint_references.append(checkpoint_chunk_writer.write(checkpoint))
            return
        graph_checkpoints.append(checkpoint)

    if pre_step_setup is not None:
        pre_step_setup(model)
    initial_context = initialize_context(model) if initialize_context is not None else None
    initial_observables = dict(model.compute_observables())
    step_results: list[StepResult] = []
    step_family_extensions: list[dict[str, dict[str, Any]]] = []
    event_family_extensions_by_step: list[list[dict[str, dict[str, Any]]]] = []
    if (
        graph_checkpoint_capture_config is not None
        and graph_checkpoint_capture_config.include_initial
    ):
        record_graph_checkpoint(
            export_grcv3_graph_checkpoint(
                model,
                identity=run_identity,
                checkpoint_id="step-00000000",
                checkpoint_label="initial",
                checkpoint_reason="initial",
                event_step_range={"start_step_inclusive": 0, "end_step_inclusive": 0},
                event_count_window=0,
                event_counts_by_kind_window={},
                include_flow_overlays=graph_checkpoint_capture_config.include_flow_overlays,
            )
        )

    last_checkpoint_step_index = 0
    event_counts_since_checkpoint: dict[str, int] = {}
    event_count_since_checkpoint = 0
    for _ in range(num_steps):
        step_result = model.step()
        step_results.append(step_result)
        step_family_extensions.append(build_step_family_extension(model))
        event_family_extensions_by_step.append(
            [
                dict(
                    grcv3_event_family_extensions(
                        classify_grcv3_event_extension(event.kind, event.payload)
                    )
                )
                for event in step_result.events
            ]
        )
        for event in step_result.events:
            event_counts_since_checkpoint[event.kind] = (
                event_counts_since_checkpoint.get(event.kind, 0) + 1
            )
        event_count_since_checkpoint += len(step_result.events)
        if graph_checkpoint_capture_config is None:
            continue
        should_capture = False
        checkpoint_label = "interval"
        checkpoint_reason = "interval"
        if graph_checkpoint_capture_config.every_step:
            should_capture = True
        elif (
            graph_checkpoint_capture_config.every_n_steps is not None
            and step_result.step_index % graph_checkpoint_capture_config.every_n_steps == 0
        ):
            should_capture = True
        if (
            graph_checkpoint_capture_config.include_final
            and step_result.step_index == num_steps
        ):
            should_capture = True
            checkpoint_label = "final"
            checkpoint_reason = "final"
        if not should_capture:
            continue
        record_graph_checkpoint(
            export_grcv3_graph_checkpoint(
                model,
                identity=run_identity,
                checkpoint_id=f"step-{step_result.step_index:08d}",
                checkpoint_label=checkpoint_label,
                checkpoint_reason=checkpoint_reason,
                event_step_range={
                    "start_step_inclusive": last_checkpoint_step_index + 1,
                    "end_step_inclusive": step_result.step_index,
                },
                event_count_window=event_count_since_checkpoint,
                event_counts_by_kind_window=dict(sorted(event_counts_since_checkpoint.items())),
                include_flow_overlays=graph_checkpoint_capture_config.include_flow_overlays,
            )
        )
        last_checkpoint_step_index = step_result.step_index
        event_counts_since_checkpoint = {}
        event_count_since_checkpoint = 0

    final_observables = dict(model.compute_observables())
    graph_checkpoint_index = (
        GraphCheckpointIndex(
            identity=run_identity,
            selection_policy=graph_checkpoint_capture_config.selection_policy,
            selection_params=graph_checkpoint_capture_config.selection_params,
            checkpoints=tuple(streamed_checkpoint_references),
        )
        if streamed_checkpoint_references
        else None
    )
    return GRCV3LaneRunArtifacts(
        model=model,
        initial_observables=initial_observables,
        step_results=step_results,
        final_observables=final_observables,
        step_family_extensions=step_family_extensions,
        event_family_extensions_by_step=event_family_extensions_by_step,
        graph_checkpoints=graph_checkpoints,
        graph_checkpoint_index=graph_checkpoint_index,
        artifact_layout=streamed_artifact_layout,
        graph_checkpoint_capture_config=graph_checkpoint_capture_config,
        initial_context=initial_context,
    )
