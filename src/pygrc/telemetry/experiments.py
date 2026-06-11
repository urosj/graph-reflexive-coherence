"""Representative telemetry-backed experiment helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pygrc.core import (
    BACKEND_SELECTIONS_KEY,
    GRCParams,
    WeightedGraphBackend,
    build_backend_selection,
    build_backend_selection_payload,
    digest_snapshot,
)
from pygrc.models import (
    DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    GRC9,
    GRC9LandscapeRunResult,
    GRCV3,
    build_grc9_from_landscape_seed,
    build_grcv3_from_landscape_seed,
    resolve_grc9_landscape_params,
    run_grcv2_landscape_seed,
    run_grc9_landscape_seed,
    run_grcv3_landscape_seed,
)
from pygrc.models.grc_9_checkpoints import export_grc9_graph_checkpoint

from ._experiment_defaults import (
    DEFAULT_CELL1_SEED,
    DEFAULT_CELL4_SEED,
    DEFAULT_GRC9_DIAGNOSTIC_PROBE_NAME,
    DEFAULT_GRC9_LANDSCAPE_EXPERIMENT_PATH,
    DEFAULT_GRC9_LANDSCAPE_PROFILE,
    DEFAULT_GRC9_LANDSCAPE_SOURCE_REFERENCE,
    DEFAULT_GRC9_LANDSCAPE_STEPS,
    DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
    DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
    DEFAULT_GRC9_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_GRC9_REPRESENTATIVE_LANE,
    DEFAULT_GRC9_REPRESENTATIVE_SOURCE_REFERENCE,
    DEFAULT_GRC9_REPRESENTATIVE_STEPS,
    DEFAULT_GRCV3_BROAD_COLLAPSE_SURVEY_LANES,
    DEFAULT_GRCV3_CANDIDATE_TRANSITION_BASELINE_SEED,
    DEFAULT_GRCV3_CANDIDATE_TRANSITION_COMPARISON_SEED,
    DEFAULT_GRCV3_CANDIDATE_TRANSITION_STEPS,
    DEFAULT_GRCV3_COLLAPSE_TRACE_DIRECT_SEED,
    DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
    DEFAULT_GRCV3_COLLAPSE_TRACE_PATH_SEED,
    DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_DIRECT_SEED,
    DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_PATH_SEED,
    DEFAULT_GRCV3_COLLAPSE_TRACE_STEPS,
    DEFAULT_GRCV3_LANDSCAPE_EXPERIMENT_PATH,
    DEFAULT_GRCV3_LANDSCAPE_STEPS,
    DEFAULT_GRCV3_PATH_FAILURE_TRACE_BASELINE_SEED,
    DEFAULT_GRCV3_PATH_FAILURE_TRACE_COMPARISON_SEED,
    DEFAULT_GRCV3_PATH_FAILURE_TRACE_STEPS,
    DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BASELINE_SEED,
    DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BLOCKED_CONTROL_SEED,
    DEFAULT_GRCV3_POST_SPARK_COLLAPSE_REFINED_CONTROL_SEED,
    DEFAULT_GRCV3_POST_SPARK_COLLAPSE_STEPS,
    DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_START_STEP,
    DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_STEPS,
    DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_BASELINE_SEED,
    DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_COMPARISON_SEED,
    DEFAULT_GRCV3_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_GRCV3_REPRESENTATIVE_LANE,
    DEFAULT_GRCV3_REPRESENTATIVE_SOURCE_REFERENCE,
    DEFAULT_GRCV3_REPRESENTATIVE_STEPS,
    DEFAULT_GRCV3_SETTLEMENT_LOCUS_BASELINE_SEED,
    DEFAULT_GRCV3_SETTLEMENT_LOCUS_COMPARISON_SEED,
    DEFAULT_GRCV3_SETTLEMENT_LOCUS_STEPS,
    DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED,
    DEFAULT_GRCV3_SETTLEMENT_REENTRY_COMPARISON_SEED,
    DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS,
    DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_REPRESENTATIVE_FAMILY,
    DEFAULT_REPRESENTATIVE_RNG_SEED,
    DEFAULT_REPRESENTATIVE_STEPS,
)
from ._grcv3_collapse_traces import (
    build_grcv3_landscape_broad_collapse_survey as _build_grcv3_landscape_broad_collapse_survey,
    build_grcv3_landscape_collapse_lane_trace as _build_grcv3_landscape_collapse_lane_trace,
    build_grcv3_landscape_collapse_regime_trace as _build_grcv3_landscape_collapse_regime_trace,
    build_grcv3_landscape_post_collapse_geometry_exclusion_trace as _build_grcv3_landscape_post_collapse_geometry_exclusion_trace,
    build_grcv3_landscape_post_spark_collapse_boundary_trace as _build_grcv3_landscape_post_spark_collapse_boundary_trace,
    build_grcv3_landscape_post_spark_delay_authorability_trace as _build_grcv3_landscape_post_spark_delay_authorability_trace,
    build_grcv3_landscape_post_spark_late_window_stability_trace as _build_grcv3_landscape_post_spark_late_window_stability_trace,
    build_grcv3_landscape_pre_spark_collapse_decomposition_trace as _build_grcv3_landscape_pre_spark_collapse_decomposition_trace,
)
from ._grcv3_extensions import (
    _build_grcv3_backend_summary,
    _build_grcv3_basin_summary,
    _build_grcv3_choice_state,
    _build_grcv3_hierarchy_state,
    _build_grcv3_landscape_run_summary,
    _build_grcv3_landscape_step_observability,
    _build_grcv3_lifecycle_event_counts,
    _build_grcv3_run_summary_extension,
    _build_grcv3_signed_hessian,
    _build_grcv3_spark_state,
    _build_grcv3_step_extension,
)
from ._grcv3_failure_traces import (
    build_grcv3_landscape_candidate_transition_trace as _build_grcv3_landscape_candidate_transition_trace,
    build_grcv3_landscape_path_failure_trace as _build_grcv3_landscape_path_failure_trace,
    build_grcv3_landscape_settlement_locus_regime_trace as _build_grcv3_landscape_settlement_locus_regime_trace,
)
from ._grcv3_lane_runner import (
    GRCV3CheckpointConfig,
    run_grcv3_lane_with_telemetry,
)
from ._grcv3_settlement_traces import (
    build_grcv3_landscape_secondary_support_authorability_trace as _build_grcv3_landscape_secondary_support_authorability_trace,
    build_grcv3_landscape_settlement_reentry_neighborhood_trace as _build_grcv3_landscape_settlement_reentry_neighborhood_trace,
    build_grcv3_landscape_settlement_reentry_secondary_support_counterfactual_trace as _build_grcv3_landscape_settlement_reentry_secondary_support_counterfactual_trace,
    build_grcv3_landscape_settlement_reentry_support_isolation_trace as _build_grcv3_landscape_settlement_reentry_support_isolation_trace,
    build_grcv3_landscape_settlement_reentry_trace as _build_grcv3_landscape_settlement_reentry_trace,
)
from ._grc9_extensions import (
    _build_grc9_event_extension,
    _build_grc9_run_summary_extension,
    _build_grc9_step_extension,
    _capture_grc9_identity_fission_observation,
)
from ._experiment_results import (
    GRC9LandscapeExperimentResult,
    GRC9RepresentativeExperimentResult,
    GRC9RepresentativeRunResult,
    GRCV2RepresentativeExperimentResult,
    GRCV3LandscapeExperimentResult,
    GRCV3RepresentativeExperimentResult,
    GRCV3RepresentativeRunResult,
)
from .compare import compare_run_summaries
from .grcv3_contract import (
    GRCV3TransientLandscapeStepSummary,
    grcv3_run_summary_family_extensions,
    grcv3_step_family_extensions,
)
from .grc9_contract import (
    GRC9LaneContext,
    GRC9_TELEMETRY_CONTRACT_VERSION as _PHASE_T_GRC9_CONTRACT_VERSION,
    grc9_event_family_extensions,
    grc9_run_summary_family_extensions,
    grc9_step_family_extensions,
)
from .io import (
    DEFAULT_TELEMETRY_ROOT,
    GraphCheckpointChunkWriter,
    TelemetryArtifactLayout,
    build_telemetry_artifact_layout,
    save_comparison_report,
    save_experiment_report,
)
from .recorder import (
    GraphCheckpointCaptureConfig,
    TelemetryCaptureConfig,
    TelemetryCaptureResult,
    capture_run_telemetry,
)
from .reports import build_run_experiment_report
from .schema import (
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    build_run_id,
)
from ._telemetry_utils import _to_plain_data


_GRC9_TELEMETRY_FAMILY = "grc9"
_GRC9_TELEMETRY_CONTRACT_VERSION = "phase6_iter10_v1"
_GRC9_ABUNDANCE_CONTRACT = "topology_updated_current_flux_diagnostic"
_GRC9_LANDSCAPE_LOWERING_MODE = "structural_graph_graft_v1"


class _GRC9CheckpointCapture:
    """Collect optional graph checkpoints for one GRC9 experiment lane."""

    def __init__(
        self,
        *,
        model: GRC9,
        run_identity: RunTelemetryIdentity,
        checkpoint_config: GraphCheckpointCaptureConfig | None,
        telemetry_root: str | Path,
        telemetry_experiment_path: str | Path,
    ) -> None:
        self._model = model
        self._run_identity = run_identity
        self._checkpoint_config = checkpoint_config
        self._last_checkpoint_step_index = 0
        self._event_count_since_checkpoint = 0
        self._event_counts_since_checkpoint: dict[str, int] = {}
        self._graph_checkpoints: list[Any] = []
        self._streamed_checkpoint_references: list[GraphCheckpointReference] = []
        self._artifact_layout: TelemetryArtifactLayout | None = None
        self._checkpoint_chunk_writer: GraphCheckpointChunkWriter | None = None
        if (
            checkpoint_config is not None
            and checkpoint_config.storage_mode == "jsonl_chunks"
        ):
            self._artifact_layout = build_telemetry_artifact_layout(
                run_identity.run_id,
                root_dir=telemetry_root,
                experiment_path=telemetry_experiment_path,
            )
            self._checkpoint_chunk_writer = GraphCheckpointChunkWriter(
                self._artifact_layout,
                chunk_size=checkpoint_config.chunk_size,
            )

    @property
    def graph_checkpoints(self) -> tuple[Any, ...]:
        return tuple(self._graph_checkpoints)

    @property
    def graph_checkpoint_index(self) -> GraphCheckpointIndex | None:
        if (
            self._checkpoint_config is None
            or not self._streamed_checkpoint_references
        ):
            return None
        return GraphCheckpointIndex(
            identity=self._run_identity,
            selection_policy=self._checkpoint_config.selection_policy,
            selection_params=self._checkpoint_config.selection_params,
            checkpoints=tuple(self._streamed_checkpoint_references),
        )

    @property
    def artifact_layout(self) -> TelemetryArtifactLayout | None:
        return self._artifact_layout

    def maybe_record_initial(self) -> None:
        if self._checkpoint_config is None or not self._checkpoint_config.include_initial:
            return
        self._record_checkpoint(
            checkpoint_id="step-00000000",
            checkpoint_label="initial",
            checkpoint_reason="initial",
            event_step_range={"start_step_inclusive": 0, "end_step_inclusive": 0},
            event_count_window=0,
            event_counts_by_kind_window={},
        )

    def observe_step(self, step_result: Any) -> None:
        if self._checkpoint_config is None:
            return
        for event in step_result.events:
            self._event_counts_since_checkpoint[event.kind] = (
                self._event_counts_since_checkpoint.get(event.kind, 0) + 1
            )
        self._event_count_since_checkpoint += len(step_result.events)

        should_capture = False
        checkpoint_label = "interval"
        checkpoint_reason = "interval"
        if self._checkpoint_config.every_step:
            should_capture = True
        elif (
            self._checkpoint_config.every_n_steps is not None
            and step_result.step_index % self._checkpoint_config.every_n_steps == 0
        ):
            should_capture = True
        if (
            self._checkpoint_config.include_final
            and step_result.step_index == self._run_identity.requested_steps
        ):
            should_capture = True
            checkpoint_label = "final"
            checkpoint_reason = "final"
        if not should_capture:
            return

        self._record_checkpoint(
            checkpoint_id=f"step-{step_result.step_index:08d}",
            checkpoint_label=checkpoint_label,
            checkpoint_reason=checkpoint_reason,
            event_step_range={
                "start_step_inclusive": self._last_checkpoint_step_index + 1,
                "end_step_inclusive": step_result.step_index,
            },
            event_count_window=self._event_count_since_checkpoint,
            event_counts_by_kind_window=dict(
                sorted(self._event_counts_since_checkpoint.items())
            ),
        )
        self._last_checkpoint_step_index = step_result.step_index
        self._event_count_since_checkpoint = 0
        self._event_counts_since_checkpoint = {}

    def _record_checkpoint(
        self,
        *,
        checkpoint_id: str,
        checkpoint_label: str,
        checkpoint_reason: str,
        event_step_range: Mapping[str, int],
        event_count_window: int,
        event_counts_by_kind_window: Mapping[str, int],
    ) -> None:
        assert self._checkpoint_config is not None
        checkpoint = export_grc9_graph_checkpoint(
            self._model,
            identity=self._run_identity,
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            checkpoint_reason=checkpoint_reason,
            event_step_range=event_step_range,
            event_count_window=event_count_window,
            event_counts_by_kind_window=event_counts_by_kind_window,
            include_flow_overlays=self._checkpoint_config.include_flow_overlays,
        )
        if self._checkpoint_chunk_writer is not None:
            self._streamed_checkpoint_references.append(
                self._checkpoint_chunk_writer.write(checkpoint)
            )
            return
        self._graph_checkpoints.append(checkpoint)


def _build_grc9_checkpoint_capture_config(
    *,
    record_graph_checkpoints: bool,
    checkpoint_every_step: bool,
    checkpoint_every_n_steps: int | None,
    checkpoint_storage_mode: str | None,
    checkpoint_chunk_size: int,
    include_flow_overlays: bool,
) -> GraphCheckpointCaptureConfig | None:
    if not record_graph_checkpoints:
        return None
    storage_mode = (
        checkpoint_storage_mode
        if checkpoint_storage_mode is not None
        else ("jsonl_chunks" if checkpoint_every_step else "per_checkpoint_files")
    )
    return GraphCheckpointCaptureConfig(
        include_initial=True,
        include_final=True,
        every_step=checkpoint_every_step,
        every_n_steps=checkpoint_every_n_steps,
        include_flow_overlays=include_flow_overlays,
        storage_mode=storage_mode,
        chunk_size=checkpoint_chunk_size,
    )


def run_grcv2_representative_experiment(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH,
    family_name: str = DEFAULT_REPRESENTATIVE_FAMILY,
    num_steps: int = DEFAULT_REPRESENTATIVE_STEPS,
    rng_seed: int | None = DEFAULT_REPRESENTATIVE_RNG_SEED,
    record_graph_checkpoints: bool = False,
    checkpoint_every_step: bool = False,
    checkpoint_every_n_steps: int | None = None,
    checkpoint_storage_mode: str | None = None,
    checkpoint_chunk_size: int = 100,
    include_flow_overlays: bool = False,
    cell1_seed_path: str | Path = DEFAULT_CELL1_SEED,
    cell4_seed_path: str | Path = DEFAULT_CELL4_SEED,
) -> GRCV2RepresentativeExperimentResult:
    """Run the first canonical telemetry-backed `GRCV2` experiment surface.

    By default this records the behavior-facing artifact lane only:
    step rows, event rows, run summaries, and report sidecars. Graph checkpoint
    artifacts remain opt-in through `record_graph_checkpoints` and the
    associated checkpoint-cadence/storage flags.
    """

    resolved_cell1_seed_path = Path(cell1_seed_path)
    resolved_cell4_seed_path = Path(cell4_seed_path)
    base_experiment_path = Path(telemetry_experiment_path) / family_name

    cell1_run = run_grcv2_landscape_seed(
        resolved_cell1_seed_path,
        family_name=family_name,
        rng_seed=rng_seed,
        num_steps=num_steps,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=base_experiment_path / "cell-1",
        record_graph_checkpoints=record_graph_checkpoints,
        checkpoint_every_step=checkpoint_every_step,
        checkpoint_every_n_steps=checkpoint_every_n_steps,
        checkpoint_storage_mode=checkpoint_storage_mode,
        checkpoint_chunk_size=checkpoint_chunk_size,
        include_flow_overlays=include_flow_overlays,
    )
    cell4_run = run_grcv2_landscape_seed(
        resolved_cell4_seed_path,
        family_name=family_name,
        rng_seed=rng_seed,
        num_steps=num_steps,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=base_experiment_path / "cell-4",
        record_graph_checkpoints=record_graph_checkpoints,
        checkpoint_every_step=checkpoint_every_step,
        checkpoint_every_n_steps=checkpoint_every_n_steps,
        checkpoint_storage_mode=checkpoint_storage_mode,
        checkpoint_chunk_size=checkpoint_chunk_size,
        include_flow_overlays=include_flow_overlays,
    )

    assert cell1_run.telemetry is not None
    assert cell4_run.telemetry is not None

    cell1_report = build_run_experiment_report(
        cell1_run.telemetry.run_summary,
        step_rows=cell1_run.telemetry.step_rows,
        artifact_layout=cell1_run.telemetry.artifact_layout,
    )
    cell4_report = build_run_experiment_report(
        cell4_run.telemetry.run_summary,
        step_rows=cell4_run.telemetry.step_rows,
        artifact_layout=cell4_run.telemetry.artifact_layout,
    )
    comparison_report = compare_run_summaries(
        cell1_run.telemetry.run_summary,
        cell4_run.telemetry.run_summary,
        left_artifact_layout=cell1_run.telemetry.artifact_layout,
        right_artifact_layout=cell4_run.telemetry.artifact_layout,
    )

    if cell1_run.telemetry.artifact_layout is not None:
        save_experiment_report(
            cell1_run.telemetry.artifact_layout.experiment_report_path,
            cell1_report,
        )
        save_comparison_report(
            cell1_run.telemetry.artifact_layout.comparison_report_path,
            comparison_report,
        )
    if cell4_run.telemetry.artifact_layout is not None:
        save_experiment_report(
            cell4_run.telemetry.artifact_layout.experiment_report_path,
            cell4_report,
        )
        save_comparison_report(
            cell4_run.telemetry.artifact_layout.comparison_report_path,
            comparison_report,
        )

    return GRCV2RepresentativeExperimentResult(
        family_name=family_name,
        num_steps=num_steps,
        rng_seed=rng_seed,
        cell1_seed_path=resolved_cell1_seed_path,
        cell4_seed_path=resolved_cell4_seed_path,
        cell1_run=cell1_run,
        cell4_run=cell4_run,
        cell1_report=cell1_report,
        cell4_report=cell4_report,
        comparison_report=comparison_report,
    )


def run_grc9_representative_experiment(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRC9_REPRESENTATIVE_EXPERIMENT_PATH,
    lane_name: str = DEFAULT_GRC9_REPRESENTATIVE_LANE,
    num_steps: int = DEFAULT_GRC9_REPRESENTATIVE_STEPS,
    record_graph_checkpoints: bool = False,
    checkpoint_every_step: bool = False,
    checkpoint_every_n_steps: int | None = None,
    checkpoint_storage_mode: str | None = None,
    checkpoint_chunk_size: int = 100,
    include_flow_overlays: bool = False,
) -> GRC9RepresentativeExperimentResult:
    """Run the representative telemetry-backed Phase 6 GRC9 lane.

    The baseline lane is intentionally synthetic and replay-oriented:
    it starts from one deterministic mechanical substrate that emits spark and
    expansion on the first step, then exposes growth on later steps.
    """

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0 for the representative GRC9 lane")

    checkpoint_config = _build_grc9_checkpoint_capture_config(
        record_graph_checkpoints=record_graph_checkpoints,
        checkpoint_every_step=checkpoint_every_step,
        checkpoint_every_n_steps=checkpoint_every_n_steps,
        checkpoint_storage_mode=checkpoint_storage_mode,
        checkpoint_chunk_size=checkpoint_chunk_size,
        include_flow_overlays=include_flow_overlays,
    )

    primary_model = _build_grc9_representative_model()
    replay_model = GRC9.from_state(
        primary_model.get_state(),
        _to_plain_data(primary_model.get_params().raw_config),
    )
    base_experiment_path = Path(telemetry_experiment_path) / lane_name

    primary_run = _run_grc9_representative_lane(
        model=primary_model,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=base_experiment_path / "primary",
        lane_name=lane_name,
        role="primary",
        num_steps=num_steps,
        checkpoint_config=checkpoint_config,
    )
    replay_run = _run_grc9_representative_lane(
        model=replay_model,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=base_experiment_path / "replay",
        lane_name=lane_name,
        role="replay",
        num_steps=num_steps,
        checkpoint_config=checkpoint_config,
    )

    primary_report = build_run_experiment_report(
        primary_run.telemetry.run_summary,
        step_rows=primary_run.telemetry.step_rows,
        artifact_layout=primary_run.telemetry.artifact_layout,
    )
    replay_report = build_run_experiment_report(
        replay_run.telemetry.run_summary,
        step_rows=replay_run.telemetry.step_rows,
        artifact_layout=replay_run.telemetry.artifact_layout,
    )
    comparison_report = compare_run_summaries(
        primary_run.telemetry.run_summary,
        replay_run.telemetry.run_summary,
        left_artifact_layout=primary_run.telemetry.artifact_layout,
        right_artifact_layout=replay_run.telemetry.artifact_layout,
    )

    if primary_run.telemetry.artifact_layout is not None:
        save_experiment_report(
            primary_run.telemetry.artifact_layout.experiment_report_path,
            primary_report,
        )
        save_comparison_report(
            primary_run.telemetry.artifact_layout.comparison_report_path,
            comparison_report,
        )
    if replay_run.telemetry.artifact_layout is not None:
        save_experiment_report(
            replay_run.telemetry.artifact_layout.experiment_report_path,
            replay_report,
        )
        save_comparison_report(
            replay_run.telemetry.artifact_layout.comparison_report_path,
            comparison_report,
        )

    return GRC9RepresentativeExperimentResult(
        lane_name=lane_name,
        num_steps=num_steps,
        primary_run=primary_run,
        replay_run=replay_run,
        primary_report=primary_report,
        replay_report=replay_report,
        comparison_report=comparison_report,
    )


def run_grc9_landscape_experiment(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRC9_LANDSCAPE_EXPERIMENT_PATH,
    profile_name: str = DEFAULT_GRC9_LANDSCAPE_PROFILE,
    num_steps: int = DEFAULT_GRC9_LANDSCAPE_STEPS,
    record_graph_checkpoints: bool = False,
    checkpoint_every_step: bool = False,
    checkpoint_every_n_steps: int | None = None,
    checkpoint_storage_mode: str | None = None,
    checkpoint_chunk_size: int = 100,
    include_flow_overlays: bool = False,
    cell1_seed_path: str | Path = DEFAULT_CELL1_SEED,
    cell4_seed_path: str | Path = DEFAULT_CELL4_SEED,
    overrides: dict[str, Any] | None = None,
) -> GRC9LandscapeExperimentResult:
    """Run the canonical seed-driven structural GRC9 cell-1/cell-4 lane."""

    checkpoint_config = _build_grc9_checkpoint_capture_config(
        record_graph_checkpoints=record_graph_checkpoints,
        checkpoint_every_step=checkpoint_every_step,
        checkpoint_every_n_steps=checkpoint_every_n_steps,
        checkpoint_storage_mode=checkpoint_storage_mode,
        checkpoint_chunk_size=checkpoint_chunk_size,
        include_flow_overlays=include_flow_overlays,
    )

    resolved_cell1_seed_path = Path(cell1_seed_path)
    resolved_cell4_seed_path = Path(cell4_seed_path)
    base_experiment_path = Path(telemetry_experiment_path) / profile_name

    cell1_params = resolve_grc9_landscape_params(
        resolved_cell1_seed_path,
        overrides=overrides,
    )
    cell4_params = resolve_grc9_landscape_params(
        resolved_cell4_seed_path,
        overrides=overrides,
    )
    cell1_run = run_grc9_landscape_seed(
        resolved_cell1_seed_path,
        params=cell1_params,
        num_steps=num_steps,
    )
    cell4_run = run_grc9_landscape_seed(
        resolved_cell4_seed_path,
        params=cell4_params,
        num_steps=num_steps,
    )

    cell1_run.telemetry = _capture_grc9_landscape_run(
        run=cell1_run,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=base_experiment_path / "cell-1",
        profile_name=profile_name,
        num_steps=num_steps,
        checkpoint_config=checkpoint_config,
    )
    cell4_run.telemetry = _capture_grc9_landscape_run(
        run=cell4_run,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=base_experiment_path / "cell-4",
        profile_name=profile_name,
        num_steps=num_steps,
        checkpoint_config=checkpoint_config,
    )

    assert cell1_run.telemetry is not None
    assert cell4_run.telemetry is not None
    cell1_report = build_run_experiment_report(
        cell1_run.telemetry.run_summary,
        step_rows=cell1_run.telemetry.step_rows,
        artifact_layout=cell1_run.telemetry.artifact_layout,
    )
    cell4_report = build_run_experiment_report(
        cell4_run.telemetry.run_summary,
        step_rows=cell4_run.telemetry.step_rows,
        artifact_layout=cell4_run.telemetry.artifact_layout,
    )
    comparison_report = compare_run_summaries(
        cell1_run.telemetry.run_summary,
        cell4_run.telemetry.run_summary,
        left_artifact_layout=cell1_run.telemetry.artifact_layout,
        right_artifact_layout=cell4_run.telemetry.artifact_layout,
    )

    if cell1_run.telemetry.artifact_layout is not None:
        save_experiment_report(
            cell1_run.telemetry.artifact_layout.experiment_report_path,
            cell1_report,
        )
        save_comparison_report(
            cell1_run.telemetry.artifact_layout.comparison_report_path,
            comparison_report,
        )
    if cell4_run.telemetry.artifact_layout is not None:
        save_experiment_report(
            cell4_run.telemetry.artifact_layout.experiment_report_path,
            cell4_report,
        )
        save_comparison_report(
            cell4_run.telemetry.artifact_layout.comparison_report_path,
            comparison_report,
        )

    return GRC9LandscapeExperimentResult(
        profile_name=profile_name,
        num_steps=num_steps,
        cell1_seed_path=resolved_cell1_seed_path,
        cell4_seed_path=resolved_cell4_seed_path,
        cell1_run=cell1_run,
        cell4_run=cell4_run,
        cell1_report=cell1_report,
        cell4_report=cell4_report,
        comparison_report=comparison_report,
    )


def run_grcv3_representative_experiment(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRCV3_REPRESENTATIVE_EXPERIMENT_PATH,
    lane_name: str = DEFAULT_GRCV3_REPRESENTATIVE_LANE,
    num_steps: int = DEFAULT_GRCV3_REPRESENTATIVE_STEPS,
    record_graph_checkpoints: bool = False,
    checkpoint_every_step: bool = False,
    checkpoint_every_n_steps: int | None = None,
    checkpoint_storage_mode: str | None = None,
    checkpoint_chunk_size: int = 100,
    include_flow_overlays: bool = False,
) -> GRCV3RepresentativeExperimentResult:
    """Run the first telemetry-backed representative GRCV3 lane.

    The first truthful comparison surface is deterministic replay:
    one `primary` run and one `replay` run launched from the same initial
    Phase 5 representative state.
    """

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0 for the representative GRCV3 lane")

    primary_model = _build_grcv3_representative_model()
    replay_model = GRCV3.from_state(
        primary_model.get_state(),
        _to_plain_data(primary_model.get_params().raw_config),
    )
    base_experiment_path = Path(telemetry_experiment_path) / lane_name
    checkpoint_config = GRCV3CheckpointConfig(
        record_graph_checkpoints=record_graph_checkpoints,
        checkpoint_every_step=checkpoint_every_step,
        checkpoint_every_n_steps=checkpoint_every_n_steps,
        checkpoint_storage_mode=checkpoint_storage_mode,
        checkpoint_chunk_size=checkpoint_chunk_size,
        include_flow_overlays=include_flow_overlays,
    )

    primary_run = _run_grcv3_representative_lane(
        model=primary_model,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=base_experiment_path / "primary",
        lane_name=lane_name,
        role="primary",
        num_steps=num_steps,
        checkpoint_config=checkpoint_config,
    )
    replay_run = _run_grcv3_representative_lane(
        model=replay_model,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=base_experiment_path / "replay",
        lane_name=lane_name,
        role="replay",
        num_steps=num_steps,
        checkpoint_config=checkpoint_config,
    )

    primary_report = build_run_experiment_report(
        primary_run.telemetry.run_summary,
        step_rows=primary_run.telemetry.step_rows,
        artifact_layout=primary_run.telemetry.artifact_layout,
    )
    replay_report = build_run_experiment_report(
        replay_run.telemetry.run_summary,
        step_rows=replay_run.telemetry.step_rows,
        artifact_layout=replay_run.telemetry.artifact_layout,
    )
    comparison_report = compare_run_summaries(
        primary_run.telemetry.run_summary,
        replay_run.telemetry.run_summary,
        left_artifact_layout=primary_run.telemetry.artifact_layout,
        right_artifact_layout=replay_run.telemetry.artifact_layout,
    )

    if primary_run.telemetry.artifact_layout is not None:
        save_experiment_report(
            primary_run.telemetry.artifact_layout.experiment_report_path,
            primary_report,
        )
        save_comparison_report(
            primary_run.telemetry.artifact_layout.comparison_report_path,
            comparison_report,
        )
    if replay_run.telemetry.artifact_layout is not None:
        save_experiment_report(
            replay_run.telemetry.artifact_layout.experiment_report_path,
            replay_report,
        )
        save_comparison_report(
            replay_run.telemetry.artifact_layout.comparison_report_path,
            comparison_report,
        )

    return GRCV3RepresentativeExperimentResult(
        lane_name=lane_name,
        num_steps=num_steps,
        primary_run=primary_run,
        replay_run=replay_run,
        primary_report=primary_report,
        replay_report=replay_report,
        comparison_report=comparison_report,
    )


def run_grcv3_landscape_experiment(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRCV3_LANDSCAPE_EXPERIMENT_PATH,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    num_steps: int = DEFAULT_GRCV3_LANDSCAPE_STEPS,
    cell1_seed_path: str | Path = DEFAULT_CELL1_SEED,
    cell4_seed_path: str | Path = DEFAULT_CELL4_SEED,
    overrides: dict[str, Any] | None = None,
    record_graph_checkpoints: bool = False,
    checkpoint_every_step: bool = False,
    checkpoint_every_n_steps: int | None = None,
    checkpoint_storage_mode: str | None = None,
    checkpoint_chunk_size: int = 100,
    include_flow_overlays: bool = False,
) -> GRCV3LandscapeExperimentResult:
    """Run the canonical seed-driven GRCV3 cell-1/cell-4 behavior lane."""

    resolved_cell1_seed_path = Path(cell1_seed_path)
    resolved_cell4_seed_path = Path(cell4_seed_path)
    base_experiment_path = Path(telemetry_experiment_path) / profile_name

    cell1_run = run_grcv3_landscape_seed(
        resolved_cell1_seed_path,
        profile_name=profile_name,
        num_steps=num_steps,
        overrides=overrides,
    )
    cell4_run = run_grcv3_landscape_seed(
        resolved_cell4_seed_path,
        profile_name=profile_name,
        num_steps=num_steps,
        overrides=overrides,
    )
    checkpoint_config = GRCV3CheckpointConfig(
        record_graph_checkpoints=record_graph_checkpoints,
        checkpoint_every_step=checkpoint_every_step,
        checkpoint_every_n_steps=checkpoint_every_n_steps,
        checkpoint_storage_mode=checkpoint_storage_mode,
        checkpoint_chunk_size=checkpoint_chunk_size,
        include_flow_overlays=include_flow_overlays,
    )

    cell1_run.telemetry = _capture_grcv3_landscape_run(
        run=cell1_run,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=base_experiment_path / "cell-1",
        num_steps=num_steps,
        overrides=overrides,
        checkpoint_config=checkpoint_config,
    )
    cell4_run.telemetry = _capture_grcv3_landscape_run(
        run=cell4_run,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=base_experiment_path / "cell-4",
        num_steps=num_steps,
        overrides=overrides,
        checkpoint_config=checkpoint_config,
    )

    assert cell1_run.telemetry is not None
    assert cell4_run.telemetry is not None
    cell1_report = build_run_experiment_report(
        cell1_run.telemetry.run_summary,
        step_rows=cell1_run.telemetry.step_rows,
        artifact_layout=cell1_run.telemetry.artifact_layout,
    )
    cell4_report = build_run_experiment_report(
        cell4_run.telemetry.run_summary,
        step_rows=cell4_run.telemetry.step_rows,
        artifact_layout=cell4_run.telemetry.artifact_layout,
    )
    comparison_report = compare_run_summaries(
        cell1_run.telemetry.run_summary,
        cell4_run.telemetry.run_summary,
        left_artifact_layout=cell1_run.telemetry.artifact_layout,
        right_artifact_layout=cell4_run.telemetry.artifact_layout,
    )

    if cell1_run.telemetry.artifact_layout is not None:
        save_experiment_report(
            cell1_run.telemetry.artifact_layout.experiment_report_path,
            cell1_report,
        )
        save_comparison_report(
            cell1_run.telemetry.artifact_layout.comparison_report_path,
            comparison_report,
        )
    if cell4_run.telemetry.artifact_layout is not None:
        save_experiment_report(
            cell4_run.telemetry.artifact_layout.experiment_report_path,
            cell4_report,
        )
        save_comparison_report(
            cell4_run.telemetry.artifact_layout.comparison_report_path,
            comparison_report,
        )

    return GRCV3LandscapeExperimentResult(
        profile_name=profile_name,
        num_steps=num_steps,
        cell1_seed_path=resolved_cell1_seed_path,
        cell4_seed_path=resolved_cell4_seed_path,
        cell1_run=cell1_run,
        cell4_run=cell4_run,
        cell1_report=cell1_report,
        cell4_report=cell4_report,
        comparison_report=comparison_report,
    )


def build_grcv3_landscape_path_failure_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_PATH_FAILURE_TRACE_BASELINE_SEED,
    comparison_seed_path: str | Path = DEFAULT_GRCV3_PATH_FAILURE_TRACE_COMPARISON_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_PATH_FAILURE_TRACE_STEPS,
) -> dict[str, Any]:
    return _build_grcv3_landscape_path_failure_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )


def build_grcv3_landscape_candidate_transition_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_CANDIDATE_TRANSITION_BASELINE_SEED,
    comparison_seed_path: str | Path = DEFAULT_GRCV3_CANDIDATE_TRANSITION_COMPARISON_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_CANDIDATE_TRANSITION_STEPS,
) -> dict[str, Any]:
    return _build_grcv3_landscape_candidate_transition_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )


def build_grcv3_landscape_settlement_locus_regime_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_LOCUS_BASELINE_SEED,
    comparison_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_LOCUS_COMPARISON_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_SETTLEMENT_LOCUS_STEPS,
) -> dict[str, Any]:
    return _build_grcv3_landscape_settlement_locus_regime_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )


def build_grcv3_landscape_collapse_lane_trace(
    *,
    seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str,
    num_steps: int,
    epsilon_choice: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    epsilon_collapse: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
) -> dict[str, Any]:
    return _build_grcv3_landscape_collapse_lane_trace(
        seed_path=seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )


def build_grcv3_landscape_broad_collapse_survey(
    *,
    lane_specs: tuple[Mapping[str, Any], ...] = DEFAULT_GRCV3_BROAD_COLLAPSE_SURVEY_LANES,
    epsilon_choice: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    epsilon_collapse: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
) -> dict[str, Any]:
    return _build_grcv3_landscape_broad_collapse_survey(
        lane_specs=lane_specs,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )


def build_grcv3_landscape_pre_spark_collapse_decomposition_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_BASELINE_SEED,
    comparison_seed_path: str | Path = DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_COMPARISON_SEED,
    baseline_profile_name: str = "hot_exploratory",
    comparison_profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    baseline_primitive_id: str = "decision_core",
    comparison_primitive_id: str = "core_basin",
    baseline_num_steps: int = 10,
    comparison_num_steps: int = 160,
    epsilon_choice: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    epsilon_collapse: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
) -> dict[str, Any]:
    return _build_grcv3_landscape_pre_spark_collapse_decomposition_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        baseline_profile_name=baseline_profile_name,
        comparison_profile_name=comparison_profile_name,
        baseline_primitive_id=baseline_primitive_id,
        comparison_primitive_id=comparison_primitive_id,
        baseline_num_steps=baseline_num_steps,
        comparison_num_steps=comparison_num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )


def build_grcv3_landscape_post_spark_collapse_boundary_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BASELINE_SEED,
    blocked_control_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BLOCKED_CONTROL_SEED,
    refined_control_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_REFINED_CONTROL_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_STEPS,
    epsilon_choice: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    epsilon_collapse: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
) -> dict[str, Any]:
    return _build_grcv3_landscape_post_spark_collapse_boundary_trace(
        baseline_seed_path=baseline_seed_path,
        blocked_control_seed_path=blocked_control_seed_path,
        refined_control_seed_path=refined_control_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )


def build_grcv3_landscape_post_spark_late_window_stability_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BASELINE_SEED,
    blocked_control_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BLOCKED_CONTROL_SEED,
    refined_control_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_REFINED_CONTROL_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_STEPS,
    late_window_start_step: int = DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_START_STEP,
    epsilon_choice: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    epsilon_collapse: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
) -> dict[str, Any]:
    return _build_grcv3_landscape_post_spark_late_window_stability_trace(
        baseline_seed_path=baseline_seed_path,
        blocked_control_seed_path=blocked_control_seed_path,
        refined_control_seed_path=refined_control_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        late_window_start_step=late_window_start_step,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )


def build_grcv3_landscape_post_spark_delay_authorability_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BASELINE_SEED,
    blocked_control_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BLOCKED_CONTROL_SEED,
    refined_control_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_REFINED_CONTROL_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_STEPS,
    late_window_start_step: int = DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_START_STEP,
    epsilon_choice: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    epsilon_collapse: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
) -> dict[str, Any]:
    return _build_grcv3_landscape_post_spark_delay_authorability_trace(
        baseline_seed_path=baseline_seed_path,
        blocked_control_seed_path=blocked_control_seed_path,
        refined_control_seed_path=refined_control_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        late_window_start_step=late_window_start_step,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )


def build_grcv3_landscape_post_collapse_geometry_exclusion_trace(
    *,
    blocked_control_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BLOCKED_CONTROL_SEED,
    refined_control_seed_path: str | Path = DEFAULT_GRCV3_POST_SPARK_COLLAPSE_REFINED_CONTROL_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_STEPS,
    late_window_start_step: int = DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_START_STEP,
    epsilon_choice: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    epsilon_collapse: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
) -> dict[str, Any]:
    return _build_grcv3_landscape_post_collapse_geometry_exclusion_trace(
        blocked_control_seed_path=blocked_control_seed_path,
        refined_control_seed_path=refined_control_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        late_window_start_step=late_window_start_step,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )


def build_grcv3_landscape_collapse_regime_trace(
    *,
    direct_seed_path: str | Path = DEFAULT_GRCV3_COLLAPSE_TRACE_DIRECT_SEED,
    path_seed_path: str | Path = DEFAULT_GRCV3_COLLAPSE_TRACE_PATH_SEED,
    split_path_seed_path: str | Path = DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_PATH_SEED,
    split_direct_seed_path: str | Path = DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_DIRECT_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_COLLAPSE_TRACE_STEPS,
    epsilon_choice: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    epsilon_collapse: float = DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
) -> dict[str, Any]:
    return _build_grcv3_landscape_collapse_regime_trace(
        direct_seed_path=direct_seed_path,
        path_seed_path=path_seed_path,
        split_path_seed_path=split_path_seed_path,
        split_direct_seed_path=split_direct_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )


def build_grcv3_landscape_settlement_reentry_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED,
    comparison_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_REENTRY_COMPARISON_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS,
) -> dict[str, Any]:
    return _build_grcv3_landscape_settlement_reentry_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )


def build_grcv3_landscape_settlement_reentry_neighborhood_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED,
    comparison_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_REENTRY_COMPARISON_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS,
) -> dict[str, Any]:
    return _build_grcv3_landscape_settlement_reentry_neighborhood_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )


def build_grcv3_landscape_settlement_reentry_support_isolation_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED,
    comparison_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_REENTRY_COMPARISON_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS,
) -> dict[str, Any]:
    return _build_grcv3_landscape_settlement_reentry_support_isolation_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )


def build_grcv3_landscape_settlement_reentry_secondary_support_counterfactual_trace(
    *,
    baseline_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED,
    comparison_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_REENTRY_COMPARISON_SEED,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS,
) -> dict[str, Any]:
    return _build_grcv3_landscape_settlement_reentry_secondary_support_counterfactual_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )


def build_grcv3_landscape_secondary_support_authorability_trace(
    *,
    structural_path_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED,
    explicit_path_seed_path: str | Path = Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-path-node-split-child-inheriting-settlement-probe.seed.yaml",
    structural_direct_seed_path: str | Path = DEFAULT_GRCV3_SETTLEMENT_LOCUS_BASELINE_SEED,
    explicit_direct_seed_path: str | Path = Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-carrier-site-split-child-inheriting-settlement-probe.seed.yaml",
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int = DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS,
) -> dict[str, Any]:
    return _build_grcv3_landscape_secondary_support_authorability_trace(
        structural_path_seed_path=structural_path_seed_path,
        explicit_path_seed_path=explicit_path_seed_path,
        structural_direct_seed_path=structural_direct_seed_path,
        explicit_direct_seed_path=explicit_direct_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )


def _run_grc9_representative_lane(
    *,
    model: GRC9,
    telemetry_root: str | Path,
    telemetry_experiment_path: str | Path,
    lane_name: str,
    role: str,
    num_steps: int,
    checkpoint_config: GraphCheckpointCaptureConfig | None,
) -> GRC9RepresentativeRunResult:
    params = model.get_params()
    step_results: list[Any] = []
    rich_grc9_extensions = lane_name == DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE
    step_family_extensions: list[Mapping[str, Mapping[str, Any]]] = []
    event_family_extensions_by_step: list[list[Mapping[str, Mapping[str, Any]]]] = []
    identity_fission_observations: list[Mapping[str, Any]] = []
    run_identity = _build_grc9_representative_run_identity(
        params=params,
        lane_name=lane_name,
        role=role,
        num_steps=num_steps,
    )
    graph_capture = _GRC9CheckpointCapture(
        model=model,
        run_identity=run_identity,
        checkpoint_config=checkpoint_config,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=telemetry_experiment_path,
    )
    initial_observables = dict(model.compute_observables())
    graph_capture.maybe_record_initial()
    for _ in range(num_steps):
        step_result = model.step()
        step_results.append(step_result)
        if rich_grc9_extensions:
            lane_context = _build_grc9_representative_lane_context(
                lane_name=lane_name,
                role=role,
            )
            step_family_extensions.append(
                grc9_step_family_extensions(
                    _build_grc9_step_extension(model, lane_context=lane_context)
                )
            )
            identity_fission_observations.append(
                _capture_grc9_identity_fission_observation(model)
            )
            event_family_extensions_by_step.append(
                [
                    grc9_event_family_extensions(
                        _build_grc9_event_extension(
                            model,
                            event,
                            lane_context=lane_context,
                        )
                    )
                    for event in step_result.events
                ]
            )
        graph_capture.observe_step(step_result)
    final_observables = dict(model.compute_observables())

    if rich_grc9_extensions:
        lane_context = _build_grc9_representative_lane_context(
            lane_name=lane_name,
            role=role,
        )
        shared_family_extensions = {}
        summary_family_extensions = grc9_run_summary_family_extensions(
            _build_grc9_run_summary_extension(
                model,
                step_results,
                lane_context=lane_context,
                identity_fission_observations=identity_fission_observations,
            )
        )
    else:
        shared_family_extensions = {
            _GRC9_TELEMETRY_FAMILY: {
                "contract_version": _GRC9_TELEMETRY_CONTRACT_VERSION,
                "lane_name": lane_name,
                "role": role,
                "abundance_contract": _GRC9_ABUNDANCE_CONTRACT,
                "source_reference": DEFAULT_GRC9_REPRESENTATIVE_SOURCE_REFERENCE,
            }
        }
        summary_family_extensions = {
            _GRC9_TELEMETRY_FAMILY: {
                "contract_version": _GRC9_TELEMETRY_CONTRACT_VERSION,
                "lane_name": lane_name,
                "role": role,
                "abundance_contract": _GRC9_ABUNDANCE_CONTRACT,
                "source_reference": DEFAULT_GRC9_REPRESENTATIVE_SOURCE_REFERENCE,
                "final_expansion_count": len(model.get_state().expansion_registry),
            }
        }
    telemetry = capture_run_telemetry(
        model_family=_GRC9_TELEMETRY_FAMILY,
        params_identity=params.params_hash,
        seed_name=f"{lane_name}_{role}",
        seed_source_reference=DEFAULT_GRC9_REPRESENTATIVE_SOURCE_REFERENCE,
        seed_path=f"synthetic/grc9/{lane_name}/{role}",
        param_family=None,
        rng_seed=int(params.evolution.get("rng_seed", 0)),
        requested_steps=num_steps,
        initial_observables=initial_observables,
        step_results=step_results,
        final_observables=final_observables,
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        family_extensions=shared_family_extensions,
        step_family_extensions=(
            step_family_extensions if rich_grc9_extensions else None
        ),
        event_family_extensions_by_step=(
            event_family_extensions_by_step if rich_grc9_extensions else None
        ),
        summary_family_extensions=summary_family_extensions,
        graph_checkpoints=graph_capture.graph_checkpoints,
        graph_checkpoint_index=graph_capture.graph_checkpoint_index,
        artifact_layout=graph_capture.artifact_layout,
        config=TelemetryCaptureConfig(
            root_dir=telemetry_root,
            experiment_path=telemetry_experiment_path,
            write_artifacts=True,
            graph_checkpoints=checkpoint_config,
        ),
    )
    return GRC9RepresentativeRunResult(
        role=role,
        seed_name=f"{lane_name}_{role}",
        model=model,
        initial_observables=initial_observables,
        step_results=step_results,
        final_observables=final_observables,
        telemetry=telemetry,
        final_snapshot_digest=digest_snapshot(model.snapshot()),
    )


def _build_grc9_representative_run_identity(
    *,
    params: GRCParams,
    lane_name: str,
    role: str,
    num_steps: int,
) -> RunTelemetryIdentity:
    seed_name = f"{lane_name}_{role}"
    seed_path = f"synthetic/grc9/{lane_name}/{role}"
    rng_seed = int(params.evolution.get("rng_seed", 0))
    return RunTelemetryIdentity(
        run_id=build_run_id(
            model_family=_GRC9_TELEMETRY_FAMILY,
            params_identity=params.params_hash,
            seed_name=seed_name,
            seed_source_reference=DEFAULT_GRC9_REPRESENTATIVE_SOURCE_REFERENCE,
            seed_path=seed_path,
            param_family=None,
            rng_seed=rng_seed,
            requested_steps=num_steps,
            overrides=None,
        ),
        model_family=_GRC9_TELEMETRY_FAMILY,
        params_identity=params.params_hash,
        seed_name=seed_name,
        seed_source_reference=DEFAULT_GRC9_REPRESENTATIVE_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family=None,
        rng_seed=rng_seed,
        requested_steps=num_steps,
    )


def _build_grc9_representative_lane_context(
    *,
    lane_name: str,
    role: str,
) -> GRC9LaneContext:
    return GRC9LaneContext(
        source_reference="implementation/Phase-T-GRC9-TelemetryContract.md",
        seed_source_reference=DEFAULT_GRC9_REPRESENTATIVE_SOURCE_REFERENCE,
        lane_name=lane_name,
        role=role,
    )


def build_grc9_diagnostic_probe() -> Mapping[str, Any]:
    """Build a synthetic paper-facing GRC9 diagnostic probe payload."""

    lane_context = GRC9LaneContext(
        source_reference="implementation/Phase-T-GRC9-TelemetryContract.md",
        seed_source_reference="synthetic/grc9/diagnostic-probe",
        lane_name=DEFAULT_GRC9_DIAGNOSTIC_PROBE_NAME,
        role="diagnostic_probe",
    )
    model = _build_grc9_diagnostic_probe_model()
    step_result = model.step()
    _inject_identity_fission_candidate_probe_state(model)
    first_fission_observation = _capture_grc9_identity_fission_observation(model)
    second_fission_observation = dict(first_fission_observation)
    second_fission_observation["step_index"] = int(
        first_fission_observation.get("step_index", 0)
    ) + 1
    fission_observations = (
        first_fission_observation,
        second_fission_observation,
    )
    coarse_checks = _build_grc9_coarse_reconstruction_checks(model)
    step_extension = grc9_step_family_extensions(
        _build_grc9_step_extension(model, lane_context=lane_context)
    )["grc9"]
    run_summary = grc9_run_summary_family_extensions(
        _build_grc9_run_summary_extension(
            model,
            (step_result,),
            lane_context=lane_context,
            identity_fission_observations=fission_observations,
            identity_fission_persistence_delta=2,
            identity_fission_min_basin_mass=0.0,
        )
    )["grc9"]
    sign_crossing_events = _build_grc9_sign_crossing_probe_events(lane_context)

    return {
        "probe_name": DEFAULT_GRC9_DIAGNOSTIC_PROBE_NAME,
        "contract_version": _PHASE_T_GRC9_CONTRACT_VERSION,
        "lane_context": lane_context.to_mapping(),
        "step_extension": step_extension,
        "run_summary_extension": run_summary,
        "sign_crossing_event_extensions": sign_crossing_events,
        "coarse_reconstruction_checks": coarse_checks,
        "diagnostic_status": {
            "scale_weighted_abundance": "artifact_backed",
            "identity_fission_candidate": "diagnostic_only",
            "identity_fission_confirmed": "artifact_backed",
            "sign_crossing": (
                "artifact_backed" if sign_crossing_events else "reserved_future"
            ),
            "spark_calibration": "diagnostic_only",
            "coarse_reconstruction": "artifact_backed",
        },
        "runtime_gaps": {
            "near_saturation_extension": "reserved_future",
            "boundary_horizon": "reserved_future",
            "ternary_tree_depth_histograms": "reserved_future",
            "frc_sigma_field": "reserved_future",
            "observer_views": "reserved_future",
            "grc9v3_semantics": "out_of_scope",
            "grcl9_lowering": "out_of_scope",
            "lorentzian_causal_layer": "out_of_scope",
        },
    }


def _build_grc9_diagnostic_probe_model() -> GRC9:
    base_model = _build_grc9_representative_model()
    config = _to_plain_data(base_model.get_params().raw_config)
    evolution = dict(config.get("evolution", {}))
    evolution["scale_weighted_abundance_gamma"] = 2.0
    evolution["spark_threshold_mode"] = "calibrated_fraction"
    evolution["burn_in_M_H"] = 0.125
    evolution["burn_in_M_C"] = 0.0625
    config["evolution"] = evolution
    return GRC9.from_state(base_model.get_state(), config)


def _inject_identity_fission_candidate_probe_state(model: GRC9) -> None:
    state = model.get_state()
    if not state.expansion_registry:
        return
    expansion_record = next(iter(state.expansion_registry.values()))
    candidate_sinks = tuple(expansion_record.module_node_ids[1:3])
    if len(candidate_sinks) < 2:
        return
    state.sink_set = set(candidate_sinks)
    state.basins = {
        candidate_sinks[0]: {candidate_sinks[0]},
        candidate_sinks[1]: {candidate_sinks[1]},
    }


def _build_grc9_coarse_reconstruction_checks(model: GRC9) -> Mapping[str, Any]:
    checks: dict[str, Any] = {}
    for field_name in ("conductance", "signed_flux"):
        coarse_state = model.coarse_grain_columns(field_name)
        reconstructed = model.split_columns(coarse_state)["port_field"]
        original = _grc9_probe_port_field(model, field_name)
        checks[field_name] = {
            "mode": coarse_state.get("mode"),
            "max_abs_error": _max_port_field_abs_error(original, reconstructed),
        }
    return checks


def _grc9_probe_port_field(model: GRC9, field_name: str) -> Mapping[str, Mapping[str, float]]:
    state = model.get_state()
    field: dict[str, dict[str, float]] = {
        str(node_id): {str(port_id): 0.0 for port_id in range(1, 10)}
        for node_id in sorted(state.topology.iter_live_node_ids())
    }
    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        port_edge = state.port_edges[edge_id]
        if field_name == "conductance":
            value_a = value_b = float(port_edge.conductance)
        elif field_name == "signed_flux":
            value_a = float(port_edge.flux_uv)
            value_b = -float(port_edge.flux_uv)
        else:
            value_a = value_b = 0.0
        field[str(endpoint_a[0])][str(endpoint_a[1] + 1)] = value_a
        field[str(endpoint_b[0])][str(endpoint_b[1] + 1)] = value_b
    return field


def _max_port_field_abs_error(
    original: Mapping[str, Mapping[str, float]],
    reconstructed: Mapping[str, Mapping[str, float]],
) -> float:
    max_error = 0.0
    node_ids = sorted(set(original) | set(reconstructed), key=int)
    for node_id in node_ids:
        original_ports = original.get(node_id, {})
        reconstructed_ports = reconstructed.get(node_id, {})
        port_ids = sorted(set(original_ports) | set(reconstructed_ports), key=int)
        for port_id in port_ids:
            max_error = max(
                max_error,
                abs(
                    float(original_ports.get(port_id, 0.0))
                    - float(reconstructed_ports.get(port_id, 0.0))
                ),
            )
    return float(max_error)


def _build_grc9_sign_crossing_probe_events(
    lane_context: GRC9LaneContext,
) -> list[Mapping[str, Any]]:
    sign_model = _build_grc9_sign_crossing_probe_model()
    events = sign_model._detect_events()
    return [
        grc9_event_family_extensions(
            _build_grc9_event_extension(
                sign_model,
                event,
                lane_context=lane_context,
            )
        )["grc9"]
        for event in events
        if event.kind == "spark"
        and event.payload.get("spark_kind") == "saturation_sign_crossing"
    ]


def _build_grc9_sign_crossing_probe_model() -> GRC9:
    connections = [(edge_id, 0, edge_id, edge_id + 1, 0) for edge_id in range(9)]
    port_edges = {
        str(edge_id): {
            "node_u": 0,
            "port_u": edge_id + 1,
            "node_v": edge_id + 1,
            "port_v": 1,
            "conductance": 1.0,
            "flux_uv": 0.0,
        }
        for edge_id in range(9)
    }
    return GRC9.from_state(
        state={
            "topology": _build_port_topology_snapshot(connections),
            "node_coherence": {
                "0": 10.0,
                "1": 9.0,
                "2": 11.0,
                "3": 12.0,
                "4": 9.0,
                "5": 11.0,
                "6": 12.0,
                "7": 9.0,
                "8": 11.0,
                "9": 12.0,
            },
            "sink_set": [0],
            "prev_column_diagnostic": {"0": [1.0, 1.0, 1.0]},
            "port_edges": port_edges,
        },
        params={
            "dt": 0.1,
            "evolution": {
                "tau_instability": 999.0,
                "eps_spark": 0.0,
                "enable_sign_crossing_spark": True,
                "D_eff_target": 30,
            },
            "constitutive_semantic_modes": {
                "frame_mode": "fixed_port_chart",
                "curvature_backend": "none",
                "boundary_mode": "prune",
                "expansion_distribution_mode": "equal",
                "edge_label_selection": "all",
            },
        },
    )


def _capture_grc9_landscape_run(
    *,
    run: GRC9LandscapeRunResult,
    telemetry_root: str | Path,
    telemetry_experiment_path: str | Path,
    profile_name: str,
    num_steps: int,
    checkpoint_config: GraphCheckpointCaptureConfig | None,
) -> TelemetryCaptureResult:
    seed_path = run.request.seed_path
    seed_source_reference = run.request.seed.meta.source_reference
    rich_grc9_extensions = profile_name == DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE
    run_identity = _build_grc9_landscape_run_identity(
        run=run,
        profile_name=profile_name,
        num_steps=num_steps,
    )
    graph_capture: _GRC9CheckpointCapture | None = None
    if rich_grc9_extensions or checkpoint_config is not None:
        replay_model = build_grc9_from_landscape_seed(
            run.request.seed,
            params=run.request.params,
            validate_seed=False,
        )
        graph_capture = _GRC9CheckpointCapture(
            model=replay_model,
            run_identity=run_identity,
            checkpoint_config=checkpoint_config,
            telemetry_root=telemetry_root,
            telemetry_experiment_path=telemetry_experiment_path,
        )
        graph_capture.maybe_record_initial()
        replay_step_results: list[Any] = []
        step_family_extensions_list: list[Mapping[str, Mapping[str, Any]]] = []
        event_family_extensions_list: list[list[Mapping[str, Mapping[str, Any]]]] = []
        identity_fission_observations: list[Mapping[str, Any]] = []
        lane_context = (
            _build_grc9_landscape_lane_context(
                profile_name=profile_name,
                seed_source_reference=seed_source_reference,
            )
            if rich_grc9_extensions
            else None
        )
        for expected_step_result in run.step_results:
            replay_step_result = replay_model.step()
            if len(replay_step_result.events) != len(expected_step_result.events):
                raise ValueError("GRC9 landscape replay event count mismatch")
            replay_step_results.append(replay_step_result)
            if lane_context is not None:
                step_family_extensions_list.append(
                    grc9_step_family_extensions(
                        _build_grc9_step_extension(
                            replay_model,
                            lane_context=lane_context,
                        )
                    )
                )
                identity_fission_observations.append(
                    _capture_grc9_identity_fission_observation(replay_model)
                )
                event_family_extensions_list.append(
                    [
                        grc9_event_family_extensions(
                            _build_grc9_event_extension(
                                replay_model,
                                event,
                                lane_context=lane_context,
                            )
                        )
                        for event in replay_step_result.events
                    ]
                )
            graph_capture.observe_step(replay_step_result)
    if rich_grc9_extensions:
        assert lane_context is not None
        step_family_extensions = step_family_extensions_list
        event_family_extensions_by_step = event_family_extensions_list
        summary_family_extensions = grc9_run_summary_family_extensions(
            _build_grc9_run_summary_extension(
                replay_model,
                replay_step_results,
                lane_context=lane_context,
                identity_fission_observations=identity_fission_observations,
            )
        )
        shared_family_extensions = {}
    else:
        step_family_extensions = None
        event_family_extensions_by_step = None
        shared_family_extensions = {
            _GRC9_TELEMETRY_FAMILY: {
                "contract_version": _GRC9_TELEMETRY_CONTRACT_VERSION,
                "profile_name": profile_name,
                "abundance_contract": _GRC9_ABUNDANCE_CONTRACT,
                "seed_source_reference": seed_source_reference,
                "source_reference": DEFAULT_GRC9_LANDSCAPE_SOURCE_REFERENCE,
                "source_lowering_mode": _GRC9_LANDSCAPE_LOWERING_MODE,
            }
        }
        summary_family_extensions = {
            _GRC9_TELEMETRY_FAMILY: {
                "contract_version": _GRC9_TELEMETRY_CONTRACT_VERSION,
                "profile_name": profile_name,
                "abundance_contract": _GRC9_ABUNDANCE_CONTRACT,
                "seed_source_reference": seed_source_reference,
                "source_reference": DEFAULT_GRC9_LANDSCAPE_SOURCE_REFERENCE,
                "source_lowering_mode": _GRC9_LANDSCAPE_LOWERING_MODE,
                "final_expansion_count": len(run.model.get_state().expansion_registry),
            }
        }
    return capture_run_telemetry(
        model_family=_GRC9_TELEMETRY_FAMILY,
        params_identity=run.request.params.params_hash,
        seed_name=run.request.seed.meta.name,
        seed_source_reference=seed_source_reference,
        seed_path=None if seed_path is None else str(seed_path),
        param_family=profile_name,
        rng_seed=run.request.params.evolution.get("rng_seed"),
        requested_steps=num_steps,
        initial_observables=run.initial_observables,
        step_results=run.step_results,
        final_observables=run.final_observables,
        resolved_params=run.request.params.resolved_config,
        raw_params=run.request.params.raw_config,
        family_extensions=shared_family_extensions,
        step_family_extensions=step_family_extensions,
        event_family_extensions_by_step=event_family_extensions_by_step,
        summary_family_extensions=summary_family_extensions,
        graph_checkpoints=(
            () if graph_capture is None else graph_capture.graph_checkpoints
        ),
        graph_checkpoint_index=(
            None if graph_capture is None else graph_capture.graph_checkpoint_index
        ),
        artifact_layout=None if graph_capture is None else graph_capture.artifact_layout,
        config=TelemetryCaptureConfig(
            root_dir=telemetry_root,
            experiment_path=telemetry_experiment_path,
            write_artifacts=True,
            graph_checkpoints=checkpoint_config,
        ),
    )


def _build_grc9_landscape_run_identity(
    *,
    run: GRC9LandscapeRunResult,
    profile_name: str,
    num_steps: int,
) -> RunTelemetryIdentity:
    seed_path = run.request.seed_path
    seed_path_string = None if seed_path is None else str(seed_path)
    rng_seed = run.request.params.evolution.get("rng_seed")
    return RunTelemetryIdentity(
        run_id=build_run_id(
            model_family=_GRC9_TELEMETRY_FAMILY,
            params_identity=run.request.params.params_hash,
            seed_name=run.request.seed.meta.name,
            seed_source_reference=run.request.seed.meta.source_reference,
            seed_path=seed_path_string,
            param_family=profile_name,
            rng_seed=rng_seed,
            requested_steps=num_steps,
            overrides=None,
        ),
        model_family=_GRC9_TELEMETRY_FAMILY,
        params_identity=run.request.params.params_hash,
        seed_name=run.request.seed.meta.name,
        seed_source_reference=run.request.seed.meta.source_reference,
        seed_path=seed_path_string,
        param_family=profile_name,
        rng_seed=rng_seed,
        requested_steps=num_steps,
    )


def _build_grc9_landscape_lane_context(
    *,
    profile_name: str,
    seed_source_reference: str,
) -> GRC9LaneContext:
    return GRC9LaneContext(
        source_reference="implementation/Phase-T-GRC9-TelemetryContract.md",
        profile_name=profile_name,
        seed_source_reference=seed_source_reference,
        source_lowering_mode=_GRC9_LANDSCAPE_LOWERING_MODE,
    )


def _build_grc9_representative_model() -> GRC9:
    connections = [
        (edge_id, 0, edge_id, edge_id + 1, 0)
        for edge_id in range(9)
    ] + [(9, 1, 1, 10, 0)]
    topology = _build_port_topology_snapshot(connections)
    port_edges = {
        str(edge_id): {
            "node_u": 0,
            "port_u": edge_id + 1,
            "node_v": edge_id + 1,
            "port_v": 1,
            "conductance": 0.01,
            "flux_uv": 0.0,
        }
        for edge_id in range(9)
    }
    port_edges["9"] = {
        "node_u": 1,
        "port_u": 2,
        "node_v": 10,
        "port_v": 1,
        "conductance": 1.0,
        "flux_uv": 0.0,
    }
    return GRC9.from_state(
        state={
            "topology": topology,
            "node_coherence": {
                "0": 1.0,
                **{str(node_id): 100.0 for node_id in range(1, 10)},
                "10": 0.0,
            },
            "port_edges": port_edges,
        },
        params={
            "dt": 0.1,
            "evolution": {
                "alpha": 1.0,
                "beta": 1.0,
                "gamma": 1.0,
                "delta": 1.0,
                "kappa_c": 1.0,
                "eta": 1.0,
                "tau_instability": 0.5,
                "eps_spark": 0.01,
                "D_eff_target": 30,
                "w_bond": 1.0,
                "lambda_birth": 1e9,
                "alpha_seed": 0.25,
                "rng_seed": 0,
                "site_potential_selection": "quadratic",
                "site_potential_params": {"mu": 0.0, "scale": 1.0},
            },
            "constitutive_semantic_modes": {
                "frame_mode": "fixed_port_chart",
                "curvature_backend": "none",
                "boundary_mode": "prune",
                "expansion_distribution_mode": "equal",
                "edge_label_selection": "all",
            },
        },
    )


def _build_port_topology_snapshot(
    connections: list[tuple[int, int, int, int, int]],
) -> dict[str, Any]:
    node_ids: set[int] = set()
    incidence: dict[str, list[int]] = {}
    edges: list[dict[str, Any]] = []
    for edge_id, node_a, slot_a, node_b, slot_b in connections:
        node_ids.update({node_a, node_b})
        incidence.setdefault(str(node_a), []).append(edge_id)
        incidence.setdefault(str(node_b), []).append(edge_id)
        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": node_a, "slot": slot_a},
                "endpoint_b": {"node_id": node_b, "slot": slot_b},
                "payload": {},
            }
        )
    return {
        "nodes": [{"node_id": node_id, "payload": {}} for node_id in sorted(node_ids)],
        "edges": sorted(edges, key=lambda edge: int(edge["edge_id"])),
        "incidence": {
            node_id: sorted(edge_ids) for node_id, edge_ids in sorted(incidence.items())
        },
        "port_structure": {},
    }


def _run_grcv3_representative_lane(
    *,
    model: GRCV3,
    telemetry_root: str | Path,
    telemetry_experiment_path: str | Path,
    lane_name: str,
    role: str,
    num_steps: int,
    checkpoint_config: GRCV3CheckpointConfig,
) -> GRCV3RepresentativeRunResult:
    from pygrc.telemetry import RunTelemetryIdentity, TelemetryCaptureConfig, build_run_id

    run_identity = RunTelemetryIdentity(
        run_id=build_run_id(
            model_family="grcv3",
            params_identity=model.get_params().params_hash,
            seed_name=f"{lane_name}_{role}",
            seed_source_reference=DEFAULT_GRCV3_REPRESENTATIVE_SOURCE_REFERENCE,
            seed_path=f"synthetic/grcv3/{lane_name}/{role}",
            param_family=None,
            rng_seed=None,
            requested_steps=num_steps,
            overrides=None,
        ),
        model_family="grcv3",
        params_identity=model.get_params().params_hash,
        seed_name=f"{lane_name}_{role}",
        seed_source_reference=DEFAULT_GRCV3_REPRESENTATIVE_SOURCE_REFERENCE,
        seed_path=f"synthetic/grcv3/{lane_name}/{role}",
        param_family=None,
        rng_seed=None,
        requested_steps=num_steps,
    )
    lane_artifacts = run_grcv3_lane_with_telemetry(
        model=model,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=telemetry_experiment_path,
        run_identity=run_identity,
        num_steps=num_steps,
        checkpoint_config=checkpoint_config,
        build_step_family_extension=lambda active_model: dict(
            grcv3_step_family_extensions(_build_grcv3_step_extension(active_model))
        ),
        pre_step_setup=_prepare_grcv3_lane_model,
    )
    summary_family_extensions = grcv3_run_summary_family_extensions(
        _build_grcv3_run_summary_extension(
            lane_artifacts.model,
            lane_artifacts.step_results,
        )
    )
    params = lane_artifacts.model.get_params()
    telemetry = capture_run_telemetry(
        model_family="grcv3",
        params_identity=params.params_hash,
        seed_name=f"{lane_name}_{role}",
        seed_source_reference=DEFAULT_GRCV3_REPRESENTATIVE_SOURCE_REFERENCE,
        seed_path=f"synthetic/grcv3/{lane_name}/{role}",
        param_family=None,
        rng_seed=None,
        requested_steps=num_steps,
        initial_observables=lane_artifacts.initial_observables,
        step_results=lane_artifacts.step_results,
        final_observables=lane_artifacts.final_observables,
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        step_family_extensions=lane_artifacts.step_family_extensions,
        event_family_extensions_by_step=lane_artifacts.event_family_extensions_by_step,
        summary_family_extensions=summary_family_extensions,
        graph_checkpoints=lane_artifacts.graph_checkpoints,
        graph_checkpoint_index=lane_artifacts.graph_checkpoint_index,
        artifact_layout=lane_artifacts.artifact_layout,
        config=TelemetryCaptureConfig(
            root_dir=telemetry_root,
            experiment_path=telemetry_experiment_path,
            write_artifacts=True,
            graph_checkpoints=lane_artifacts.graph_checkpoint_capture_config,
        ),
    )
    return GRCV3RepresentativeRunResult(
        role=role,
        seed_name=f"{lane_name}_{role}",
        model=lane_artifacts.model,
        initial_observables=lane_artifacts.initial_observables,
        step_results=lane_artifacts.step_results,
        final_observables=lane_artifacts.final_observables,
        telemetry=telemetry,
        final_snapshot_digest=digest_snapshot(lane_artifacts.model.snapshot()),
    )


def _build_grcv3_representative_model() -> GRCV3:
    graph = WeightedGraphBackend()
    left = graph.add_node({"kind": "representative"})
    center = graph.add_node({"kind": "representative"})
    right = graph.add_node({"kind": "representative"})
    edge_left = graph.add_edge(left, center, {"kind": "representative"})
    edge_right = graph.add_edge(center, right, {"kind": "representative"})

    model = GRCV3.from_state(
        state={
            "nodes": {
                str(left): _grcv3_node_attributes(coherence=1.2, basin_id=left),
                str(center): _grcv3_node_attributes(coherence=0.75, basin_id=center),
                str(right): _grcv3_node_attributes(coherence=0.35, basin_id=right),
            },
            "base_conductance": {
                str(edge_left): 1.0,
                str(edge_right): 1.0,
            },
        },
        params={
            "dt": 0.05,
            "evolution": {
                "eps_gradient": 1e-3,
                "eps_hessian": 1e-3,
                "eps_spark": 1e6,
                "tau_split": 2.0,
            },
            "constitutive_semantic_modes": {
                BACKEND_SELECTIONS_KEY: build_backend_selection_payload(
                    [build_backend_selection(category="choice", name="disabled")]
                )
            },
        },
    )
    model.get_state().topology = graph
    return model


def _grcv3_node_attributes(
    *,
    coherence: float,
    basin_id: str | int,
) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": [0.0, 0.0],
        "hessian": [[1.0, 0.0], [0.0, 1.0]],
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": None,
        "depth": 0,
    }


def _prepare_grcv3_lane_model(model: GRCV3) -> None:
    model.rebuild_basin_attributes()
    model.rebuild_identity_state()


def _capture_grcv3_landscape_run(
    *,
    run: GRCV3LandscapeRunResult,
    telemetry_root: str | Path,
    telemetry_experiment_path: str | Path,
    num_steps: int,
    overrides: dict[str, Any] | None,
    checkpoint_config: GRCV3CheckpointConfig,
) -> TelemetryCaptureResult:
    from pygrc.telemetry import RunTelemetryIdentity, build_run_id

    params = run.model.get_params()
    run_identity = RunTelemetryIdentity(
        run_id=build_run_id(
            model_family="grcv3",
            params_identity=params.params_hash,
            seed_name=run.request.seed.meta.name,
            seed_source_reference=run.request.seed.meta.source_reference,
            seed_path=(
                None if run.request.seed_path is None else str(run.request.seed_path)
            ),
            param_family=run.request.profile_name,
            rng_seed=None,
            requested_steps=num_steps,
            overrides=overrides,
        ),
        model_family="grcv3",
        params_identity=params.params_hash,
        seed_name=run.request.seed.meta.name,
        seed_source_reference=run.request.seed.meta.source_reference,
        seed_path=(None if run.request.seed_path is None else str(run.request.seed_path)),
        param_family=run.request.profile_name,
        rng_seed=None,
        requested_steps=num_steps,
    )
    replay_model = build_grcv3_from_landscape_seed(
        run.request.seed,
        params=_to_plain_data(params.raw_config),
        profile_name=run.request.profile_name,
        validate_seed=False,
    )
    transient_landscape_steps: list[GRCV3TransientLandscapeStepSummary | None] = []

    def build_landscape_step_family_extension(
        active_model: GRCV3,
    ) -> dict[str, dict[str, Any]]:
        transient_landscape = _build_grcv3_landscape_step_observability(active_model)
        transient_landscape_steps.append(transient_landscape)
        return dict(
            grcv3_step_family_extensions(
                _build_grcv3_step_extension(
                    active_model,
                    transient_landscape=transient_landscape,
                )
            )
        )

    lane_artifacts = run_grcv3_lane_with_telemetry(
        model=replay_model,
        telemetry_root=telemetry_root,
        telemetry_experiment_path=telemetry_experiment_path,
        run_identity=run_identity,
        num_steps=num_steps,
        checkpoint_config=checkpoint_config,
        build_step_family_extension=build_landscape_step_family_extension,
        pre_step_setup=_prepare_grcv3_lane_model,
        initialize_context=_build_grcv3_landscape_step_observability,
    )
    summary_family_extensions = grcv3_run_summary_family_extensions(
        _build_grcv3_run_summary_extension(
            run.model,
            run.step_results,
            transient_landscape=_build_grcv3_landscape_run_summary(
                run.model,
                initial_observability=lane_artifacts.initial_context,
                step_observability=tuple(transient_landscape_steps),
                step_results=run.step_results,
            ),
        )
    )
    return capture_run_telemetry(
        model_family="grcv3",
        params_identity=params.params_hash,
        seed_name=run.request.seed.meta.name,
        seed_source_reference=run.request.seed.meta.source_reference,
        seed_path=(
            None if run.request.seed_path is None else str(run.request.seed_path)
        ),
        param_family=run.request.profile_name,
        rng_seed=None,
        requested_steps=num_steps,
        initial_observables=run.initial_observables,
        step_results=run.step_results,
        final_observables=run.final_observables,
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        overrides=overrides,
        step_family_extensions=lane_artifacts.step_family_extensions,
        event_family_extensions_by_step=lane_artifacts.event_family_extensions_by_step,
        summary_family_extensions=summary_family_extensions,
        graph_checkpoints=lane_artifacts.graph_checkpoints,
        graph_checkpoint_index=lane_artifacts.graph_checkpoint_index,
        artifact_layout=lane_artifacts.artifact_layout,
        config=TelemetryCaptureConfig(
            root_dir=telemetry_root,
            experiment_path=telemetry_experiment_path,
            write_artifacts=True,
            graph_checkpoints=lane_artifacts.graph_checkpoint_capture_config,
        ),
    )

__all__ = [
    "DEFAULT_CELL1_SEED",
    "DEFAULT_CELL4_SEED",
    "DEFAULT_GRC9_DIAGNOSTIC_PROBE_NAME",
    "DEFAULT_GRC9_LANDSCAPE_EXPERIMENT_PATH",
    "DEFAULT_GRC9_LANDSCAPE_PROFILE",
    "DEFAULT_GRC9_LANDSCAPE_STEPS",
    "DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE",
    "DEFAULT_GRC9_REPRESENTATIVE_EXPERIMENT_PATH",
    "DEFAULT_GRC9_REPRESENTATIVE_LANE",
    "DEFAULT_GRC9_REPRESENTATIVE_STEPS",
    "DEFAULT_GRCV3_BROAD_COLLAPSE_SURVEY_LANES",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_DIRECT_SEED",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_PATH_SEED",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_DIRECT_SEED",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_PATH_SEED",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_STEPS",
    "DEFAULT_GRCV3_LANDSCAPE_PROFILE",
    "DEFAULT_GRCV3_REPRESENTATIVE_EXPERIMENT_PATH",
    "DEFAULT_GRCV3_LANDSCAPE_EXPERIMENT_PATH",
    "DEFAULT_GRCV3_LANDSCAPE_STEPS",
    "DEFAULT_GRCV3_PATH_FAILURE_TRACE_BASELINE_SEED",
    "DEFAULT_GRCV3_CANDIDATE_TRANSITION_BASELINE_SEED",
    "DEFAULT_GRCV3_CANDIDATE_TRANSITION_COMPARISON_SEED",
    "DEFAULT_GRCV3_CANDIDATE_TRANSITION_STEPS",
    "DEFAULT_GRCV3_SETTLEMENT_LOCUS_BASELINE_SEED",
    "DEFAULT_GRCV3_SETTLEMENT_LOCUS_COMPARISON_SEED",
    "DEFAULT_GRCV3_SETTLEMENT_LOCUS_STEPS",
    "DEFAULT_GRCV3_PATH_FAILURE_TRACE_COMPARISON_SEED",
    "DEFAULT_GRCV3_PATH_FAILURE_TRACE_STEPS",
    "DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BASELINE_SEED",
    "DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BLOCKED_CONTROL_SEED",
    "DEFAULT_GRCV3_POST_SPARK_COLLAPSE_REFINED_CONTROL_SEED",
    "DEFAULT_GRCV3_POST_SPARK_COLLAPSE_STEPS",
    "DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_START_STEP",
    "DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_STEPS",
    "DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_BASELINE_SEED",
    "DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_COMPARISON_SEED",
    "DEFAULT_GRCV3_REPRESENTATIVE_LANE",
    "DEFAULT_GRCV3_REPRESENTATIVE_STEPS",
    "DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED",
    "DEFAULT_GRCV3_SETTLEMENT_REENTRY_COMPARISON_SEED",
    "DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS",
    "DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH",
    "DEFAULT_REPRESENTATIVE_FAMILY",
    "DEFAULT_REPRESENTATIVE_RNG_SEED",
    "DEFAULT_REPRESENTATIVE_STEPS",
    "GRC9LandscapeExperimentResult",
    "GRC9RepresentativeExperimentResult",
    "GRC9RepresentativeRunResult",
    "GRCV2RepresentativeExperimentResult",
    "GRCV3LandscapeExperimentResult",
    "GRCV3RepresentativeExperimentResult",
    "GRCV3RepresentativeRunResult",
    "build_grc9_diagnostic_probe",
    "run_grc9_landscape_experiment",
    "run_grc9_representative_experiment",
    "build_grcv3_landscape_broad_collapse_survey",
    "build_grcv3_landscape_candidate_transition_trace",
    "build_grcv3_landscape_collapse_lane_trace",
    "build_grcv3_landscape_collapse_regime_trace",
    "build_grcv3_landscape_path_failure_trace",
    "build_grcv3_landscape_post_collapse_geometry_exclusion_trace",
    "build_grcv3_landscape_post_spark_collapse_boundary_trace",
    "build_grcv3_landscape_post_spark_delay_authorability_trace",
    "build_grcv3_landscape_post_spark_late_window_stability_trace",
    "build_grcv3_landscape_pre_spark_collapse_decomposition_trace",
    "build_grcv3_landscape_secondary_support_authorability_trace",
    "build_grcv3_landscape_settlement_locus_regime_trace",
    "build_grcv3_landscape_settlement_reentry_neighborhood_trace",
    "build_grcv3_landscape_settlement_reentry_secondary_support_counterfactual_trace",
    "build_grcv3_landscape_settlement_reentry_support_isolation_trace",
    "build_grcv3_landscape_settlement_reentry_trace",
    "run_grcv3_landscape_experiment",
    "run_grcv3_representative_experiment",
    "run_grcv2_representative_experiment",
]
