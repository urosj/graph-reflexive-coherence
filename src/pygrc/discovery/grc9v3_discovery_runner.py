"""Replayable generated-seed runs for GRC9V3 phenomenology discovery."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.core import digest_snapshot
from pygrc.models import GRC9V3
from pygrc.telemetry import (
    GRC9V3LaneContext,
    GRC9V3_TELEMETRY_CONTRACT_VERSION,
    GraphCheckpointArtifact,
    GraphCheckpointCaptureConfig,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    TelemetryCaptureConfig,
    TelemetryExperimentReport,
    build_run_id,
    build_telemetry_artifact_layout,
    capture_run_telemetry,
    event_rows_from_events,
    grc9v3_event_family_extensions,
    grc9v3_run_summary_family_extensions,
    grc9v3_step_family_extensions,
    save_experiment_report,
    step_row_from_step_result,
)
from pygrc.telemetry._grc9v3_extensions import (
    _build_grc9v3_event_extension,
    _build_grc9v3_run_summary_extension,
    _build_grc9v3_step_extension,
)
from scripts.run_grc9v3_representative_telemetry import _export_basic_checkpoint

from .grc9_manifest import is_session_id
from .grc9v3_hypothesis_catalog import (
    GRC9V3HypothesisCatalog,
    default_grc9v3_hypothesis_catalog,
)
from .grc9v3_seed_generator import (
    GRC9V3_COMPLEX_HYBRID_NAMES,
    GRC9V3GeneratedSeed,
    GRC9V3_PRESSURE_BOUNDARY_NAMES,
    generate_grc9v3_complex_hybrid_example,
    generate_grc9v3_pressure_boundary_example,
    generate_grc9v3_seed,
)


GRC9V3_DISCOVERY_LOW_STEP_COUNTS: Mapping[str, int] = {
    "hybrid_spark_gate": 2,
    "spark_to_expansion": 2,
    "appendix_e_cell_division": 3,
    "choice_collapse": 3,
    "growth_pressure": 3,
    "budget_preservation": 2,
    "hessian_backend_comparison": 2,
    "transport_basin_rerouting": 3,
    "coarse_cache_invalidation": 2,
    "quiescent_hybrid_control": 3,
}
GRC9V3_COMPLEX_HYBRID_STEP_COUNTS: Mapping[str, int] = {
    "complex_spark_expansion_hierarchy": 3,
    "complex_spark_expansion_choice_collapse": 3,
    "complex_expansion_growth_budget_coarse": 3,
    "complex_hessian_row_basis": 2,
    "complex_hessian_weighted_least_squares": 2,
    "complex_spark_choice_no_saturation_perturbation": 3,
    "complex_growth_low_birth_perturbation": 3,
}
GRC9V3_PRESSURE_BOUNDARY_STEP_COUNTS: Mapping[str, int] = {
    "pressure_boundary_growth_positive_control": 3,
    "pressure_boundary_growth_no_growth_control": 3,
    "generic_front_capacity_growth_comparison": 3,
    "complex_spark_expansion_pressure_boundary_growth": 4,
}

DISCOVERY_SESSION_ROOT = Path("outputs/grc9v3/phenomenology_discovery/sessions")
DISCOVERY_TRACK = "phenomenology_discovery"
DISCOVERY_PROGRAM = "grc9v3_phenomenology_discovery"
DISCOVERY_SOURCE_REFERENCE = "implementation/GRC9V3-PhenomenologyDiscovery-Plan.md"
TELEMETRY_CONTRACT_SOURCE = "implementation/Phase-T-GRC9V3-TelemetryContract.md"
CHECKPOINT_SURFACE = "phase_t_grc9v3_iter1_overlays"


@dataclass(frozen=True)
class GRC9V3DiscoveryLaneRun:
    seed: GRC9V3GeneratedSeed
    requested_steps: int
    run_id: str
    artifact_root: str
    step_count: int
    event_count: int
    event_counts_by_kind: Mapping[str, int]
    actual_event_sequence: tuple[str, ...]
    event_sequence_analysis: Mapping[str, Any]
    checkpoint_count: int
    replay_step_rows_match: bool
    replay_event_rows_match: bool
    replay_digest_match: bool
    final_observables: Mapping[str, Any]

    def to_mapping(self) -> Mapping[str, Any]:
        first_pass = _first_pass_lane_interpretation(self)
        return {
            "seed_family": self.seed.seed_family,
            "seed_name": self.seed.seed_name,
            "control_role": self.seed.control_role,
            "lane_name": self.seed.lane_name,
            "profile": self.seed.profile,
            "expected_outcome": self.seed.seed_parameters.get("expected_outcome", ""),
            "predicted_event_sequence": list(self.seed.predicted_event_sequence),
            "requested_steps": self.requested_steps,
            "run_id": self.run_id,
            "artifact_root": self.artifact_root,
            "step_count": self.step_count,
            "event_count": self.event_count,
            "event_counts_by_kind": dict(self.event_counts_by_kind),
            "actual_event_sequence": list(self.actual_event_sequence),
            "event_sequence_analysis": dict(self.event_sequence_analysis),
            "first_pass_interpretation": first_pass,
            "checkpoint_count": self.checkpoint_count,
            "replay_step_rows_match": self.replay_step_rows_match,
            "replay_event_rows_match": self.replay_event_rows_match,
            "replay_digest_match": self.replay_digest_match,
            "final_observables": dict(self.final_observables),
        }


@dataclass(frozen=True)
class GRC9V3DiscoverySessionRun:
    session_id: str
    session_root: Path
    lanes: tuple[GRC9V3DiscoveryLaneRun, ...]
    iteration: str = "I05_first_control_sessions"

    def to_mapping(self) -> Mapping[str, Any]:
        first_pass = _first_pass_session_interpretation(self.lanes)
        return {
            "session_id": self.session_id,
            "iteration": self.iteration,
            "lane_count": len(self.lanes),
            "total_steps": sum(lane.step_count for lane in self.lanes),
            "total_events": sum(lane.event_count for lane in self.lanes),
            "first_pass_interpretation": first_pass,
            "all_replay_step_rows_match": all(
                lane.replay_step_rows_match for lane in self.lanes
            ),
            "all_replay_event_rows_match": all(
                lane.replay_event_rows_match for lane in self.lanes
            ),
            "all_replay_digests_match": all(
                lane.replay_digest_match for lane in self.lanes
            ),
            "lanes": [lane.to_mapping() for lane in self.lanes],
        }


def run_grc9v3_discovery_control_session(
    *,
    session_id: str = "S0004",
    session_root: str | Path | None = None,
    step_counts: Mapping[str, int] | None = None,
    catalog: GRC9V3HypothesisCatalog | None = None,
    refined_controls: bool = False,
    appendix_e_pass_fail_controls: bool = False,
) -> GRC9V3DiscoverySessionRun:
    """Run all scheduled generated GRC9V3 control lanes with Phase T telemetry."""

    if not is_session_id(session_id):
        raise ValueError("session_id must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    lanes_root = root / "generated_lanes"
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    active_catalog = catalog or default_grc9v3_hypothesis_catalog()
    resolved_step_counts = dict(GRC9V3_DISCOVERY_LOW_STEP_COUNTS)
    resolved_step_counts.update(dict(step_counts or {}))
    planned_lane_names = tuple(
        family.seed_family
        for family in active_catalog.seed_families
        if family.scheduled_for_generation
    )
    _validate_step_count_coverage(resolved_step_counts, planned_lane_names)

    lane_results: list[GRC9V3DiscoveryLaneRun] = []
    for family in active_catalog.seed_families:
        if not family.scheduled_for_generation:
            continue
        requested_steps = int(resolved_step_counts[family.seed_family])
        for control in (*family.positive_controls, *family.negative_controls):
            seed_overrides = _seed_overrides_for_run(
                family.seed_family,
                control.control_role,
                refined_controls=refined_controls,
                appendix_e_pass_fail_controls=appendix_e_pass_fail_controls,
            )
            seed = generate_grc9v3_seed(
                family.seed_family,
                control.control_role,
                catalog=active_catalog,
                parameter_overrides=seed_overrides or None,
            )
            lane_results.append(
                _run_discovery_lane(
                    seed=seed,
                    requested_steps=requested_steps,
                    session_root=root,
                    lanes_root=lanes_root,
                )
            )

    session = GRC9V3DiscoverySessionRun(
        session_id=session_id,
        session_root=root,
        lanes=tuple(lane_results),
        iteration=(
            "I05_2_appendix_e_pass_fail_separation"
            if appendix_e_pass_fail_controls
            else (
                "I05_1_theory_first_seed_refinement"
                if refined_controls
                else "I05_first_control_sessions"
            )
        ),
    )
    _write_json(reports_root / "run_report.json", session.to_mapping())
    _write_initial_results(reports_root / "initial_results.md", session)
    _write_json(
        root / "session_manifest.json",
        _session_manifest(
            session,
            refined_controls=refined_controls,
            appendix_e_pass_fail_controls=appendix_e_pass_fail_controls,
        ),
    )
    _write_readme(
        root,
        session,
        refined_controls=refined_controls,
        appendix_e_pass_fail_controls=appendix_e_pass_fail_controls,
    )
    _append_experimental_log(
        session,
        refined_controls=refined_controls,
        appendix_e_pass_fail_controls=appendix_e_pass_fail_controls,
    )
    return session


def run_grc9v3_complex_hybrid_session(
    *,
    session_id: str = "S0008",
    session_root: str | Path | None = None,
    step_counts: Mapping[str, int] | None = None,
) -> GRC9V3DiscoverySessionRun:
    """Run connected Iteration 7 complex GRC9V3 hybrid examples."""

    if not is_session_id(session_id):
        raise ValueError("session_id must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    lanes_root = root / "generated_lanes"
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    resolved_step_counts = dict(GRC9V3_COMPLEX_HYBRID_STEP_COUNTS)
    resolved_step_counts.update(dict(step_counts or {}))
    _validate_step_count_coverage(resolved_step_counts, GRC9V3_COMPLEX_HYBRID_NAMES)

    lane_results: list[GRC9V3DiscoveryLaneRun] = []
    for example_name in GRC9V3_COMPLEX_HYBRID_NAMES:
        seed = generate_grc9v3_complex_hybrid_example(example_name)
        lane_results.append(
            _run_discovery_lane(
                seed=seed,
                requested_steps=int(resolved_step_counts[example_name]),
                session_root=root,
                lanes_root=lanes_root,
            )
        )

    session = GRC9V3DiscoverySessionRun(
        session_id=session_id,
        session_root=root,
        lanes=tuple(lane_results),
        iteration="I07_complex_hybrid_examples",
    )
    _write_json(reports_root / "run_report.json", session.to_mapping())
    _write_initial_results(reports_root / "initial_results.md", session)
    _write_json(root / "session_manifest.json", _complex_session_manifest(session))
    _write_complex_readme(root, session)
    _append_experimental_log(
        session,
        refined_controls=False,
        appendix_e_pass_fail_controls=False,
    )
    return session


def run_grc9v3_pressure_boundary_session(
    *,
    session_id: str = "S0015",
    session_root: str | Path | None = None,
    step_counts: Mapping[str, int] | None = None,
) -> GRC9V3DiscoverySessionRun:
    """Run pressure-boundary GRC9V3 evidence examples."""

    if not is_session_id(session_id):
        raise ValueError("session_id must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    lanes_root = root / "generated_lanes"
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    resolved_step_counts = dict(GRC9V3_PRESSURE_BOUNDARY_STEP_COUNTS)
    resolved_step_counts.update(dict(step_counts or {}))
    _validate_step_count_coverage(resolved_step_counts, GRC9V3_PRESSURE_BOUNDARY_NAMES)

    lane_results: list[GRC9V3DiscoveryLaneRun] = []
    for example_name in GRC9V3_PRESSURE_BOUNDARY_NAMES:
        seed = generate_grc9v3_pressure_boundary_example(example_name)
        lane_results.append(
            _run_discovery_lane(
                seed=seed,
                requested_steps=int(resolved_step_counts[example_name]),
                session_root=root,
                lanes_root=lanes_root,
            )
        )

    session = GRC9V3DiscoverySessionRun(
        session_id=session_id,
        session_root=root,
        lanes=tuple(lane_results),
        iteration="PressureBoundary_I04_2_grc9v3_pressure_boundary_evidence",
    )
    _write_json(reports_root / "run_report.json", session.to_mapping())
    _write_initial_results(reports_root / "initial_results.md", session)
    _write_json(root / "session_manifest.json", _pressure_boundary_session_manifest(session))
    _write_pressure_boundary_readme(root, session)
    _append_experimental_log(
        session,
        refined_controls=False,
        appendix_e_pass_fail_controls=False,
    )
    return session


def _seed_overrides_for_run(
    seed_family: str,
    control_role: str,
    *,
    refined_controls: bool,
    appendix_e_pass_fail_controls: bool,
) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if refined_controls or appendix_e_pass_fail_controls:
        overrides["refined_fixture"] = True
    if (
        appendix_e_pass_fail_controls
        and seed_family == "appendix_e_cell_division"
        and control_role == "negative_control"
    ):
        overrides["appendix_e_no_completion_control"] = True
    return overrides


def _validate_step_count_coverage(
    step_counts: Mapping[str, int],
    planned_lane_names: Sequence[str],
) -> None:
    missing = tuple(name for name in planned_lane_names if name not in step_counts)
    if missing:
        raise ValueError(
            "missing GRC9V3 discovery step counts for planned lanes: "
            + ", ".join(missing)
        )


def _run_discovery_lane(
    *,
    seed: GRC9V3GeneratedSeed,
    requested_steps: int,
    session_root: Path,
    lanes_root: Path,
) -> GRC9V3DiscoveryLaneRun:
    if requested_steps <= 0:
        raise ValueError("requested_steps must be > 0")
    model = GRC9V3.from_state(
        state=dict(seed.state_payload),
        params=dict(seed.expected_runtime_config),
    )
    params = model.get_params()
    seed_path = f"generated/grc9v3/phenomenology_discovery/{seed.lane_name}"
    run_identity = _run_identity(
        params_identity=params.params_hash,
        seed=seed,
        seed_path=seed_path,
        requested_steps=requested_steps,
    )
    lane_context = GRC9V3LaneContext(
        source_reference=TELEMETRY_CONTRACT_SOURCE,
        fixture_name=seed.seed_family,
        run_role=seed.control_role,
        experiment_id=session_root.name,
        representative_lane_name=seed.lane_name,
        source_runtime_artifact=DISCOVERY_SOURCE_REFERENCE,
    )
    artifact_layout = build_telemetry_artifact_layout(
        seed.lane_name,
        root_dir=lanes_root,
    )
    snapshot_dir = artifact_layout.run_dir / "snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    initial_snapshot_path = snapshot_dir / "initial_snapshot.json"
    final_snapshot_path = snapshot_dir / "final_snapshot.json"
    model.save(str(initial_snapshot_path))

    initial_observables = dict(model.compute_observables())
    primary_run = _run_rows_and_checkpoints(
        model,
        identity=run_identity,
        lane_context=lane_context,
        steps=requested_steps,
    )
    model.save(str(final_snapshot_path))
    final_digest = digest_snapshot(model.snapshot())
    final_observables = dict(model.compute_observables())

    replay_model = GRC9V3.load(str(initial_snapshot_path))
    replay_run = _run_rows_and_checkpoints(
        replay_model,
        identity=run_identity,
        lane_context=lane_context,
        steps=requested_steps,
        build_checkpoints=False,
    )
    replay_digest = digest_snapshot(replay_model.snapshot())
    replay_step_rows_match = replay_run["step_rows"] == primary_run["step_rows"]
    replay_event_rows_match = replay_run["event_rows"] == primary_run["event_rows"]
    replay_digest_match = replay_digest == final_digest

    summary_extensions = grc9v3_run_summary_family_extensions(
        _build_grc9v3_run_summary_extension(
            model,
            primary_run["step_results"],
            lane_context=lane_context,
            replay_digest_match=(
                replay_step_rows_match and replay_event_rows_match and replay_digest_match
            ),
        )
    )
    checkpoint_config = GraphCheckpointCaptureConfig(
        include_initial=True,
        include_final=True,
        every_step=True,
        include_flow_overlays=True,
        storage_mode="per_checkpoint_files",
    )
    telemetry = capture_run_telemetry(
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=seed.seed_name,
        seed_source_reference=DISCOVERY_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family=seed.profile,
        rng_seed=int(params.evolution.get("rng_seed", 0)),
        requested_steps=requested_steps,
        initial_observables=initial_observables,
        step_results=primary_run["step_results"],
        final_observables=final_observables,
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        family_extensions=_shared_family_extensions(seed, session_root.name),
        step_family_extensions=primary_run["step_family_extensions"],
        event_family_extensions_by_step=primary_run["event_family_extensions_by_step"],
        summary_family_extensions=summary_extensions,
        graph_checkpoints=primary_run["checkpoints"],
        graph_checkpoint_index=_build_checkpoint_index(
            run_identity,
            primary_run["checkpoints"],
            checkpoint_config=checkpoint_config,
        ),
        artifact_layout=artifact_layout,
        config=TelemetryCaptureConfig(
            root_dir=lanes_root,
            write_artifacts=True,
            graph_checkpoints=checkpoint_config,
        ),
    )
    experiment_report = TelemetryExperimentReport(
        family="grc9v3",
        common={
            "run_id": run_identity.run_id,
            "model_family": "grc9v3",
            "session_id": session_root.name,
            "seed_family": seed.seed_family,
            "seed_name": seed.seed_name,
            "lane_name": seed.lane_name,
            "control_role": seed.control_role,
            "profile": seed.profile,
            "requested_steps": requested_steps,
            "artifact_dir": artifact_layout.run_dir.as_posix(),
            "telemetry_dir": artifact_layout.telemetry_dir.as_posix(),
            "initial_snapshot_path": initial_snapshot_path.as_posix(),
            "final_snapshot_path": final_snapshot_path.as_posix(),
            "final_snapshot_digest": final_digest,
            "replay_final_snapshot_digest": replay_digest,
            "replay_step_rows_match": replay_step_rows_match,
            "replay_event_rows_match": replay_event_rows_match,
            "replay_digest_match": replay_digest_match,
            "checkpoint_count": len(primary_run["checkpoints"]),
        },
        extensions={
            "grc9v3": {
                "contract_version": GRC9V3_TELEMETRY_CONTRACT_VERSION,
                "discovery_session_id": session_root.name,
                "seed_parameters": dict(seed.seed_parameters),
                "expected_runtime_config": dict(seed.expected_runtime_config),
                "required_checkpoint_overlays": list(seed.required_checkpoint_overlays),
            }
        },
    )
    save_experiment_report(artifact_layout.experiment_report_path, experiment_report)

    event_counts_total = Counter(
        event.kind for step_result in primary_run["step_results"] for event in step_result.events
    )
    actual_event_sequence = tuple(
        str(event.kind)
        for step_result in primary_run["step_results"]
        for event in step_result.events
    )
    event_sequence_analysis = _event_sequence_analysis(
        predicted=seed.predicted_event_sequence,
        observed=actual_event_sequence,
    )
    assert telemetry.artifact_layout is not None
    return GRC9V3DiscoveryLaneRun(
        seed=seed,
        requested_steps=requested_steps,
        run_id=telemetry.identity.run_id,
        artifact_root=str(telemetry.artifact_layout.run_dir),
        step_count=len(telemetry.step_rows),
        event_count=len(telemetry.event_rows),
        event_counts_by_kind=dict(sorted(event_counts_total.items())),
        actual_event_sequence=actual_event_sequence,
        event_sequence_analysis=event_sequence_analysis,
        checkpoint_count=len(primary_run["checkpoints"]),
        replay_step_rows_match=replay_step_rows_match,
        replay_event_rows_match=replay_event_rows_match,
        replay_digest_match=replay_digest_match,
        final_observables=final_observables,
    )


def _run_rows_and_checkpoints(
    model: GRC9V3,
    *,
    identity: RunTelemetryIdentity,
    lane_context: GRC9V3LaneContext,
    steps: int,
    build_checkpoints: bool = True,
) -> dict[str, Any]:
    step_results: list[Any] = []
    step_rows: list[Any] = []
    event_rows: list[Any] = []
    step_family_extensions: list[Mapping[str, Mapping[str, Any]]] = []
    event_family_extensions_by_step: list[list[Mapping[str, Mapping[str, Any]]]] = []
    checkpoints: list[GraphCheckpointArtifact] = []
    if build_checkpoints:
        checkpoints.append(
            _export_discovery_checkpoint(
                model,
                identity=identity,
                checkpoint_id="step-00000000",
                checkpoint_label="initial",
                checkpoint_reason="initial",
                events=(),
                include_overlays=True,
            )
        )

    for _ in range(steps):
        step_result = model.step()
        step_results.append(step_result)
        step_extensions = grc9v3_step_family_extensions(
            _build_grc9v3_step_extension(model, lane_context=lane_context)
        )
        step_family_extensions.append(step_extensions)
        step_rows.append(
            step_row_from_step_result(
                step_result,
                identity=identity,
                family_extensions=step_extensions,
            )
        )
        resolved_event_extensions = [
            grc9v3_event_family_extensions(
                _build_grc9v3_event_extension(
                    model,
                    event,
                    lane_context=lane_context,
                )
            )
            for event in step_result.events
        ]
        event_family_extensions_by_step.append(resolved_event_extensions)
        event_rows.extend(
            event_rows_from_events(
                step_result.events,
                identity=identity,
                family_extensions_by_event=resolved_event_extensions,
            )
        )
        if build_checkpoints:
            checkpoints.append(
                _export_discovery_checkpoint(
                    model,
                    identity=identity,
                    checkpoint_id=f"step-{step_result.step_index:08d}",
                    checkpoint_label=(
                        "final" if step_result.step_index == steps else "post_step"
                    ),
                    checkpoint_reason=(
                        "final" if step_result.step_index == steps else "every_step"
                    ),
                    events=step_result.events,
                    include_overlays=True,
                )
            )
    return {
        "step_results": tuple(step_results),
        "step_rows": tuple(step_rows),
        "event_rows": tuple(event_rows),
        "step_family_extensions": tuple(step_family_extensions),
        "event_family_extensions_by_step": tuple(
            tuple(item) for item in event_family_extensions_by_step
        ),
        "checkpoints": tuple(checkpoints),
    }


def _event_sequence_analysis(
    *,
    predicted: Sequence[str],
    observed: Sequence[str],
) -> Mapping[str, Any]:
    predicted_tuple = tuple(str(item) for item in predicted)
    observed_tuple = tuple(str(item) for item in observed)
    missing_counter = Counter(predicted_tuple)
    unexpected_counter = Counter(observed_tuple)
    for kind in observed_tuple:
        if missing_counter.get(kind, 0) > 0:
            missing_counter[kind] -= 1
    for kind in predicted_tuple:
        if unexpected_counter.get(kind, 0) > 0:
            unexpected_counter[kind] -= 1
    cursor = 0
    ordered_subsequence = True
    for kind in predicted_tuple:
        try:
            cursor = observed_tuple.index(kind, cursor) + 1
        except ValueError:
            ordered_subsequence = False
            break
    exact_match = predicted_tuple == observed_tuple
    return {
        "exact_match": exact_match,
        "predicted_order_preserved": ordered_subsequence,
        "missing_predicted_event_counts": {
            kind: count for kind, count in sorted(missing_counter.items()) if count > 0
        },
        "unexpected_event_counts": {
            kind: count for kind, count in sorted(unexpected_counter.items()) if count > 0
        },
        "has_sequence_delta": not exact_match,
    }


def _export_discovery_checkpoint(
    model: GRC9V3,
    *,
    identity: RunTelemetryIdentity,
    checkpoint_id: str,
    checkpoint_label: str,
    checkpoint_reason: str,
    events: Sequence[Any],
    include_overlays: bool,
) -> GraphCheckpointArtifact:
    checkpoint = _export_basic_checkpoint(
        model,
        identity=identity,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        checkpoint_reason=checkpoint_reason,
        events=events,
        include_overlays=include_overlays,
    )
    family_extensions = {
        family: dict(payload)
        for family, payload in checkpoint.family_extensions.items()
    }
    grc9v3_payload = dict(family_extensions.get("grc9v3", {}))
    grc9v3_payload["checkpoint_surface"] = CHECKPOINT_SURFACE
    family_extensions["grc9v3"] = grc9v3_payload
    return replace(checkpoint, family_extensions=family_extensions)


def _run_identity(
    *,
    params_identity: str,
    seed: GRC9V3GeneratedSeed,
    seed_path: str,
    requested_steps: int,
) -> RunTelemetryIdentity:
    rng_seed = int(seed.expected_runtime_config["evolution"].get("rng_seed", 0))
    run_id = build_run_id(
        model_family="grc9v3",
        params_identity=params_identity,
        seed_name=seed.seed_name,
        seed_source_reference=DISCOVERY_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family=seed.profile,
        rng_seed=rng_seed,
        requested_steps=requested_steps,
        overrides={"phase_t_contract": GRC9V3_TELEMETRY_CONTRACT_VERSION},
    )
    return RunTelemetryIdentity(
        run_id=run_id,
        model_family="grc9v3",
        params_identity=params_identity,
        seed_name=seed.seed_name,
        seed_source_reference=DISCOVERY_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family=seed.profile,
        rng_seed=rng_seed,
        requested_steps=requested_steps,
    )


def _build_checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[GraphCheckpointArtifact, ...],
    *,
    checkpoint_config: GraphCheckpointCaptureConfig,
) -> GraphCheckpointIndex:
    return GraphCheckpointIndex(
        identity=identity,
        selection_policy=checkpoint_config.selection_policy,
        selection_params={
            **dict(checkpoint_config.selection_params),
            "surface": CHECKPOINT_SURFACE,
        },
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
            for checkpoint in checkpoints
        ),
        family_extensions={
            "grc9v3": {
                "contract_version": GRC9V3_TELEMETRY_CONTRACT_VERSION,
                "checkpoint_surface": CHECKPOINT_SURFACE,
            }
        },
    )


def _shared_family_extensions(
    seed: GRC9V3GeneratedSeed,
    session_id: str,
) -> Mapping[str, Mapping[str, Any]]:
    return {
        "discovery": {
            "program": DISCOVERY_PROGRAM,
            "track": DISCOVERY_TRACK,
            "session_id": session_id,
            "seed_family": seed.seed_family,
            "control_role": seed.control_role,
            "lane_name": seed.lane_name,
            "profile": seed.profile,
            "generator_version": seed.generator_version,
        }
    }


def _session_manifest(
    session: GRC9V3DiscoverySessionRun,
    *,
    refined_controls: bool,
    appendix_e_pass_fail_controls: bool,
) -> Mapping[str, Any]:
    report_path = session.session_root / "reports" / "run_report.json"
    return {
        "session_id": session.session_id,
        "program": DISCOVERY_PROGRAM,
        "family": "grc9v3",
        "track": DISCOVERY_TRACK,
        "iteration": session.iteration,
        "session_kind": "generated_run",
        "phenomenon": (
            "Appendix E pass/fail separated refined GRC9V3 seed controls"
            if appendix_e_pass_fail_controls
            else "refined scheduled GRC9V3 seed controls"
            if refined_controls
            else "all scheduled testable GRC9V3 hypotheses"
        ),
        "seed_family": "all scheduled default families",
        "control_role": "all scheduled controls",
        "status": "completed",
        "created_at": "2026-04-26",
        "git_revision": _git_revision(),
        "dirty_worktree": _dirty_worktree(),
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            "pygrc.discovery.grc9v3_discovery_runner --session-id "
            f"{session.session_id}"
            + (" --appendix-e-pass-fail-controls" if appendix_e_pass_fail_controls else "")
            + (" --refined-controls" if refined_controls else "")
        ),
        "replay_environment_note": (
            "Command records the repository virtualenv used for this run. "
            "Equivalent replays may use another Python interpreter when it has "
            "the same project dependencies and PYTHONPATH=src."
        ),
        "input_paths": [
            "src/pygrc/discovery/grc9v3_hypothesis_catalog.py",
            "src/pygrc/discovery/grc9v3_seed_generator.py",
            "outputs/grc9v3/phenomenology_discovery/generated_seed_catalog.json",
        ],
        "output_paths": [
            str(report_path),
            str(session.session_root / "reports" / "initial_results.md"),
            str(session.session_root / "generated_lanes"),
        ],
        "telemetry_paths": [lane.artifact_root for lane in session.lanes],
        "checkpoint_paths": [
            f"{lane.artifact_root}/telemetry/graph_checkpoints"
            for lane in session.lanes
        ],
        "visualization_paths": [],
        "prediction_summary": (
            "Appendix E pass/fail separated controls should preserve the completed "
            "positive division lane while making the negative lane fail completed "
            "Appendix E evidence through a real runtime precondition."
            if appendix_e_pass_fail_controls
            else (
            "Refined Iteration 5.1 controls should turn S0004 diagnostic misses "
            "into targeted choice/collapse, growth, budget, coarse-cache, "
            "transport, and Hessian evidence where the current runtime supports it."
            if refined_controls
            else (
                "Low-step Iteration 5 controls should expose immediate hybrid spark, "
                "expansion, Appendix E, choice/collapse, growth, budget, Hessian backend, "
                "transport, coarse-cache, and quiescent telemetry signatures where the "
                "current runtime can emit them."
            )
            )
        ),
        "observation_summary": (
            f"Ran {len(session.lanes)} generated GRC9V3 control lanes for "
            f"{sum(lane.step_count for lane in session.lanes)} total steps "
            f"and captured {sum(lane.event_count for lane in session.lanes)} events."
        ),
        "replay_notes": (
            "Appendix E pass/fail separation run; use this session for Appendix E "
            "selector scoring instead of S0005's non-separating negative lane."
            if appendix_e_pass_fail_controls
            else (
            "Theory-first seed refinement run; compare against S0004 smoke evidence "
            "before implementing selectors."
            if refined_controls
            else (
                "Low-step smoke discovery run for all scheduled GRC9V3 seed controls; "
                "extend selected lanes later based on selector misses."
            )
            )
        ),
        "first_pass_interpretation": _first_pass_session_interpretation(session.lanes),
    }


def _complex_session_manifest(
    session: GRC9V3DiscoverySessionRun,
) -> Mapping[str, Any]:
    report_path = session.session_root / "reports" / "run_report.json"
    return {
        "session_id": session.session_id,
        "program": DISCOVERY_PROGRAM,
        "family": "grc9v3",
        "track": DISCOVERY_TRACK,
        "iteration": session.iteration,
        "session_kind": "complex_generated_run",
        "phenomenon": "connected complex GRC9V3 hybrid examples",
        "seed_family": "complex hybrid examples",
        "control_role": "complex and perturbation controls",
        "status": "completed",
        "created_at": "2026-04-26",
        "git_revision": _git_revision(),
        "dirty_worktree": _dirty_worktree(),
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            "pygrc.discovery.grc9v3_discovery_runner --session-id "
            f"{session.session_id} --complex-hybrid-examples"
        ),
        "replay_environment_note": (
            "Command records the repository virtualenv used for this run. "
            "Equivalent replays may use another Python interpreter when it has "
            "the same project dependencies and PYTHONPATH=src."
        ),
        "input_paths": [
            "src/pygrc/discovery/grc9v3_seed_generator.py",
            "src/pygrc/discovery/grc9v3_discovery_runner.py",
        ],
        "output_paths": [
            str(report_path),
            str(session.session_root / "reports" / "initial_results.md"),
            str(session.session_root / "generated_lanes"),
        ],
        "telemetry_paths": [lane.artifact_root for lane in session.lanes],
        "checkpoint_paths": [
            f"{lane.artifact_root}/telemetry/graph_checkpoints"
            for lane in session.lanes
        ],
        "visualization_paths": [],
        "prediction_summary": (
            "Complex examples should keep mechanisms in connected graphs and "
            "exercise spark/expansion/hierarchy, spark/expansion/choice/collapse, "
            "expansion/growth/budget/coarse, paired Hessian backends, and targeted "
            "perturbations."
        ),
        "observation_summary": (
            f"Ran {len(session.lanes)} connected complex GRC9V3 lanes for "
            f"{sum(lane.step_count for lane in session.lanes)} total steps "
            f"and captured {sum(lane.event_count for lane in session.lanes)} events."
        ),
        "replay_notes": (
            "Iteration 7 pure-runtime complex examples. These are not GRCL/source "
            "claims and do not use disconnected graph unions."
        ),
        "first_pass_interpretation": _first_pass_session_interpretation(session.lanes),
    }


def _pressure_boundary_session_manifest(
    session: GRC9V3DiscoverySessionRun,
) -> Mapping[str, Any]:
    report_path = session.session_root / "reports" / "run_report.json"
    return {
        "session_id": session.session_id,
        "program": DISCOVERY_PROGRAM,
        "family": "grc9v3",
        "track": DISCOVERY_TRACK,
        "iteration": session.iteration,
        "session_kind": "pressure_boundary_generated_run",
        "phenomenon": "GRC9V3 pressure-boundary front growth",
        "seed_family": "pressure-boundary evidence examples",
        "control_role": "positive, no-growth, generic-front, and complex controls",
        "status": "completed",
        "created_at": "2026-05-02",
        "git_revision": _git_revision(),
        "dirty_worktree": _dirty_worktree(),
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            "pygrc.discovery.grc9v3_discovery_runner --session-id "
            f"{session.session_id} --pressure-boundary-examples"
        ),
        "replay_environment_note": (
            "Command records the repository virtualenv used for this run. "
            "Equivalent replays may use another Python interpreter when it has "
            "the same project dependencies and PYTHONPATH=src."
        ),
        "input_paths": [
            "src/pygrc/discovery/grc9v3_seed_generator.py",
            "src/pygrc/discovery/grc9v3_discovery_runner.py",
            "implementation/PressureBoundary-ImplementationPlan.md",
        ],
        "output_paths": [
            str(report_path),
            str(session.session_root / "reports" / "initial_results.md"),
            str(session.session_root / "generated_lanes"),
        ],
        "telemetry_paths": [lane.artifact_root for lane in session.lanes],
        "checkpoint_paths": [
            f"{lane.artifact_root}/telemetry/graph_checkpoints"
            for lane in session.lanes
        ],
        "visualization_paths": [],
        "prediction_summary": (
            "Pressure-boundary positive lanes should emit corrected "
            "front-capacity growth with pressure-boundary-specific run-summary "
            "counts. The no-growth lane should preserve pressure-boundary source "
            "metadata without emitting growth, and the generic-front comparison "
            "should emit front-capacity growth without pressure-boundary count."
        ),
        "observation_summary": (
            f"Ran {len(session.lanes)} GRC9V3 pressure-boundary lanes for "
            f"{sum(lane.step_count for lane in session.lanes)} total steps "
            f"and captured {sum(lane.event_count for lane in session.lanes)} events."
        ),
        "replay_notes": (
            "Pressure-boundary examples are pure GRC9V3 runtime fixtures. "
            "GRCL-9V3 source-backed evidence is recorded separately under "
            "`outputs/grcl9v3/lowering`."
        ),
        "first_pass_interpretation": _first_pass_session_interpretation(session.lanes),
    }


def _write_readme(
    root: Path,
    session: GRC9V3DiscoverySessionRun,
    *,
    refined_controls: bool,
    appendix_e_pass_fail_controls: bool,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {session.session_id}. "
        + (
            "GRC9V3 Appendix E Pass/Fail Separated Control Runs"
            if appendix_e_pass_fail_controls
            else
            "GRC9V3 Refined Control Runs"
            if refined_controls
            else "GRC9V3 Generated Control Runs"
        ),
        "",
        "Status: `completed`",
        "",
        (
            "This session reruns the refined controls with an Appendix E negative "
            "lane that fails completed-division evidence."
            if appendix_e_pass_fail_controls
            else
            "This session reruns all scheduled GRC9V3 discovery control lanes "
            "with theory-first seed refinements chosen after S0004."
            if refined_controls
            else (
                "This session runs all scheduled generated GRC9V3 discovery control lanes "
                "with the low step counts chosen for Iteration 5."
            )
        ),
        "",
        "Replay:",
        "",
        "```bash",
        (
            f"PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_discovery_runner --session-id {session.session_id}"
            + (" --appendix-e-pass-fail-controls" if appendix_e_pass_fail_controls else "")
            + (" --refined-controls" if refined_controls else "")
        ),
        "```",
        "",
        (
            "The replay command records the repository virtualenv used for this run; "
            "an equivalent Python environment with `PYTHONPATH=src` is also valid."
        ),
        "",
        f"Lane count: `{len(session.lanes)}`",
        f"Total steps: `{sum(lane.step_count for lane in session.lanes)}`",
        f"Total events: `{sum(lane.event_count for lane in session.lanes)}`",
        "",
        "Primary report:",
        "",
        "- `reports/run_report.json`",
        "- `reports/initial_results.md`",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_complex_readme(root: Path, session: GRC9V3DiscoverySessionRun) -> None:
    root.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {session.session_id}. GRC9V3 Complex Hybrid Examples",
        "",
        "Status: `completed`",
        "",
        "This session runs connected pure-runtime GRC9V3 examples that compose "
        "multiple mechanisms without disjoint graph unions.",
        "",
        "Replay:",
        "",
        "```bash",
        (
            f"PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_discovery_runner --session-id "
            f"{session.session_id} --complex-hybrid-examples"
        ),
        "```",
        "",
        f"Lane count: `{len(session.lanes)}`",
        f"Total steps: `{sum(lane.step_count for lane in session.lanes)}`",
        f"Total events: `{sum(lane.event_count for lane in session.lanes)}`",
        "",
        "Primary report:",
        "",
        "- `reports/run_report.json`",
        "- `reports/initial_results.md`",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_pressure_boundary_readme(root: Path, session: GRC9V3DiscoverySessionRun) -> None:
    root.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {session.session_id}. GRC9V3 Pressure-Boundary Evidence",
        "",
        "Status: `completed`",
        "",
        "This session runs pure-runtime GRC9V3 pressure-boundary front-growth "
        "examples after the 4.1 telemetry/selector cleanup.",
        "",
        "Replay:",
        "",
        "```bash",
        (
            f"PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_discovery_runner --session-id "
            f"{session.session_id} --pressure-boundary-examples"
        ),
        "```",
        "",
        f"Lane count: `{len(session.lanes)}`",
        f"Total steps: `{sum(lane.step_count for lane in session.lanes)}`",
        f"Total events: `{sum(lane.event_count for lane in session.lanes)}`",
        "",
        "Primary report:",
        "",
        "- `reports/run_report.json`",
        "- `reports/initial_results.md`",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_initial_results(path: Path, session: GRC9V3DiscoverySessionRun) -> None:
    eventful_lanes = [lane for lane in session.lanes if lane.event_count > 0]
    first_pass = _first_pass_session_interpretation(session.lanes)
    lines = [
        f"# {session.session_id} Initial Results",
        "",
        "## Scope",
        "",
        f"- {len(session.lanes)} generated control lanes",
        f"- {sum(lane.step_count for lane in session.lanes)} total simulation steps",
        f"- {sum(lane.checkpoint_count for lane in session.lanes)} GRC9V3 graph checkpoints",
        "- Every lane captured `steps.jsonl`, `events.jsonl`, `run_summary.json`, `experiment_report.json`, and graph checkpoint artifacts",
        "",
        "## Replay",
        "",
        f"- Step rows match on replay: `{all(lane.replay_step_rows_match for lane in session.lanes)}`",
        f"- Event rows match on replay: `{all(lane.replay_event_rows_match for lane in session.lanes)}`",
        f"- Final digests match on replay: `{all(lane.replay_digest_match for lane in session.lanes)}`",
        "",
        "## Event Summary",
        "",
        f"- Total events: {sum(lane.event_count for lane in session.lanes)}",
    ]
    if eventful_lanes:
        event_kinds = sorted(
            {
                kind
                for lane in eventful_lanes
                for kind in lane.event_counts_by_kind
            }
        )
        lines.append(f"- Event kinds: {', '.join(f'`{kind}`' for kind in event_kinds)}")
        lines.append("- Eventful lanes:")
        for lane in eventful_lanes:
            lines.append(f"  - `{lane.seed.lane_name}`: {lane.event_counts_by_kind}")
    else:
        lines.append("- Event kinds: none")
    sequence_deltas = [
        lane
        for lane in session.lanes
        if lane.event_sequence_analysis.get("has_sequence_delta")
    ]
    lines.extend(["", "## Event Sequence Deltas", ""])
    if sequence_deltas:
        lines.append(
            "These lanes preserve their predicted event order where possible, but "
            "also emit additional lifecycle events that must be considered during "
            "motif review:"
        )
        for lane in sequence_deltas:
            analysis = lane.event_sequence_analysis
            lines.append(
                f"- `{lane.seed.lane_name}`: predicted `{list(lane.seed.predicted_event_sequence)}`, "
                f"observed `{list(lane.actual_event_sequence)}`, "
                f"missing `{analysis['missing_predicted_event_counts']}`, "
                f"unexpected `{analysis['unexpected_event_counts']}`"
            )
    else:
        lines.append("- No predicted-vs-observed event sequence deltas.")
    lines.extend(["", "## First-Pass Control Interpretation", ""])
    lines.append(
        f"- Expected no-event lanes confirmed: `{len(first_pass['no_event_lanes_confirmed'])}`"
    )
    for lane_name in first_pass["no_event_lanes_confirmed"]:
        lines.append(f"  - `{lane_name}`")
    if first_pass["no_event_lanes_with_events"]:
        lines.append("- Expected no-event lanes with events:")
        for lane in first_pass["no_event_lanes_with_events"]:
            lines.append(
                f"  - `{lane['lane_name']}`: {lane['event_counts_by_kind']}"
            )
    if first_pass["eventful_negative_control_lanes"]:
        lines.append(
            "- Eventful negative controls needing selector-level interpretation:"
        )
        for lane in first_pass["eventful_negative_control_lanes"]:
            lines.append(
                f"  - `{lane['lane_name']}`: {lane['event_counts_by_kind']}"
            )
    if first_pass["appendix_e_negative_control_note"]:
        lines.append(
            f"- Appendix E negative control note: {first_pass['appendix_e_negative_control_note']}"
        )
    lines.extend(
        [
            "",
            "## Initial Finding",
            "",
            (
                "The Appendix E pass/fail separation run preserves the completed "
                "positive division lane and makes the negative lane fail completed "
                "Appendix E evidence. Use S0006, not S0005, for Appendix E "
                "selector pass/fail scoring."
            )
            if session.iteration == "I05_2_appendix_e_pass_fail_separation"
            else (
                "The refined controls preserve replayable telemetry/checkpoint "
                "coverage while targeting the runtime gates that S0004 missed."
            )
            if session.iteration == "I05_1_theory_first_seed_refinement"
            else (
                "The connected complex examples compose multiple runtime mechanisms "
                "without disjoint graph unions. Use the event-sequence deltas above "
                "during reviewed motif catalog work."
            )
            if session.iteration == "I07_complex_hybrid_examples"
            else (
                "The pressure-boundary examples separate pressure-boundary growth "
                "from generic corrected front-capacity growth and preserve a "
                "zero-growth pressure-boundary control for selector validation."
            )
            if session.iteration == "PressureBoundary_I04_2_grc9v3_pressure_boundary_evidence"
            else (
                "The low-step generated controls produce replayable telemetry and graph "
                "checkpoints for every scheduled GRC9V3 hypothesis. Immediate hybrid "
                "spark and expansion events fire in the saturated controls; several "
                "semantic controls remain diagnostic rather than event-emitting under "
                "these short windows."
            ),
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _first_pass_lane_interpretation(
    lane: GRC9V3DiscoveryLaneRun,
) -> Mapping[str, Any]:
    expected_outcome = str(lane.seed.seed_parameters.get("expected_outcome", ""))
    expects_no_events = lane.seed.control_role == "no_event_control"
    if not expects_no_events:
        expects_no_events = "no spark" in expected_outcome.lower()
    if not expects_no_events:
        expects_no_events = not lane.seed.predicted_event_sequence
    return {
        "expected_no_events": expects_no_events,
        "no_event_expectation_met": (
            lane.event_count == 0 if expects_no_events else None
        ),
        "negative_control_eventful": (
            lane.seed.control_role == "negative_control" and lane.event_count > 0
        ),
        "requires_selector_scoring": (
            lane.seed.control_role == "negative_control" and lane.event_count > 0
        ),
    }


def _first_pass_session_interpretation(
    lanes: Sequence[GRC9V3DiscoveryLaneRun],
) -> Mapping[str, Any]:
    no_event_confirmed: list[str] = []
    no_event_with_events: list[Mapping[str, Any]] = []
    eventful_negative_controls: list[Mapping[str, Any]] = []
    appendix_e_negative_note = ""
    for lane in lanes:
        lane_interpretation = _first_pass_lane_interpretation(lane)
        if lane_interpretation["expected_no_events"]:
            if lane.event_count == 0:
                no_event_confirmed.append(lane.seed.lane_name)
            else:
                no_event_with_events.append(
                    {
                        "lane_name": lane.seed.lane_name,
                        "event_counts_by_kind": dict(lane.event_counts_by_kind),
                    }
                )
        if lane_interpretation["negative_control_eventful"]:
            record = {
                "lane_name": lane.seed.lane_name,
                "event_counts_by_kind": dict(lane.event_counts_by_kind),
                "note": (
                    "event rows are not sufficient to accept or reject this negative "
                    "control; selector scoring must compare the mechanism-specific "
                    "predicted signatures"
                ),
            }
            eventful_negative_controls.append(record)
            if lane.seed.lane_name == "appendix_e_cell_division_negative_control":
                appendix_e_negative_note = (
                    "mechanical spark events occurred, but the negative-control claim "
                    "is daughter stabilization failure; classify it with Iteration 6 "
                    "Appendix E selectors rather than raw eventfulness."
                )
    return {
        "no_event_lanes_confirmed": sorted(no_event_confirmed),
        "no_event_lanes_with_events": no_event_with_events,
        "eventful_negative_control_lanes": eventful_negative_controls,
        "appendix_e_negative_control_note": appendix_e_negative_note,
    }


def _append_experimental_log(
    session: GRC9V3DiscoverySessionRun,
    *,
    refined_controls: bool,
    appendix_e_pass_fail_controls: bool,
) -> None:
    if session.session_root.parent.name != "sessions":
        return
    log_path = session.session_root.parent.parent / "ExperimentalLog.md"
    if not log_path.exists():
        _write_experimental_log_header(log_path)
    row = _experimental_log_row(
        session,
        refined_controls=refined_controls,
        appendix_e_pass_fail_controls=appendix_e_pass_fail_controls,
    )
    text = log_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    session_token = f"| `{session.session_id}` |"
    replaced = False
    for index, line in enumerate(lines):
        if line.startswith(session_token):
            lines[index] = row
            replaced = True
            break
    if not replaced:
        if lines and lines[-1] != "":
            lines.append(row)
        else:
            lines.append(row)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_experimental_log_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# GRC9V3 Phenomenology Discovery Experimental Log",
                "",
                "This document indexes replayable GRC9V3 phenomenology discovery sessions.",
                "",
                "Session artifacts live under:",
                "",
                "```text",
                "outputs/grc9v3/phenomenology_discovery/sessions/S0001/",
                "```",
                "",
                "Session ids are stable, zero-padded references. Categorical meaning belongs in `session_manifest.json` and index files.",
                "",
                "## Session Index",
                "",
                "| Session | Status | Kind | Iteration | Phenomenon | Seed Family | Artifact Root | Notes |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _experimental_log_row(
    session: GRC9V3DiscoverySessionRun,
    *,
    refined_controls: bool,
    appendix_e_pass_fail_controls: bool,
) -> str:
    if session.iteration == "I07_complex_hybrid_examples":
        phenomenon = "connected complex GRC9V3 hybrid examples"
        seed_family = "complex hybrid examples"
        notes = "Iteration 7 connected complex hybrid examples"
    elif session.iteration == "PressureBoundary_I04_2_grc9v3_pressure_boundary_evidence":
        phenomenon = "GRC9V3 pressure-boundary front growth evidence"
        seed_family = "pressure-boundary evidence examples"
        notes = "Pressure-boundary Iteration 4.2 GRC9V3 evidence"
    else:
        phenomenon = (
            "Appendix E pass/fail separated refined GRC9V3 seed controls"
            if appendix_e_pass_fail_controls
            else
            "refined scheduled GRC9V3 seed controls"
            if refined_controls
            else "all scheduled testable GRC9V3 hypotheses"
        )
        seed_family = "all scheduled default families"
        notes = (
            "Iteration 5.2 Appendix E pass/fail separation"
            if appendix_e_pass_fail_controls
            else
            "Iteration 5.1 theory-first seed refinement"
            if refined_controls
            else "Iteration 5 low-step generated control runs"
        )
    notes += (
        f": {len(session.lanes)} lanes, "
        f"{sum(lane.step_count for lane in session.lanes)} steps, "
        f"{sum(lane.event_count for lane in session.lanes)} events, "
        "all replay checks passed"
        if (
            all(lane.replay_step_rows_match for lane in session.lanes)
            and all(lane.replay_event_rows_match for lane in session.lanes)
            and all(lane.replay_digest_match for lane in session.lanes)
        )
        else ": replay mismatch recorded in run report"
    )
    return (
        f"| `{session.session_id}` | `completed` | `generated_run` | "
        f"`{session.iteration}` | {phenomenon} | {seed_family} | "
        f"`{session.session_root.as_posix()}/` | {notes} |"
    )


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _git_revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _dirty_worktree() -> bool:
    try:
        result = subprocess.run(
            ["git", "diff", "--quiet"],
            check=False,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode != 0
    except Exception:
        return True


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run generated GRC9V3 phenomenology discovery controls."
    )
    parser.add_argument(
        "--session-id",
        default="S0004",
        help="Replayable discovery session id, e.g. S0004.",
    )
    parser.add_argument(
        "--session-root",
        default=None,
        help="Optional explicit session root path.",
    )
    parser.add_argument(
        "--refined-controls",
        action="store_true",
        help="Run Iteration 5.1 refined controls instead of the S0004 smoke controls.",
    )
    parser.add_argument(
        "--appendix-e-pass-fail-controls",
        action="store_true",
        help=(
            "Run Iteration 5.2 refined controls with separated Appendix E "
            "positive/negative completion evidence."
        ),
    )
    parser.add_argument(
        "--complex-hybrid-examples",
        action="store_true",
        help="Run Iteration 7 connected complex hybrid examples.",
    )
    parser.add_argument(
        "--pressure-boundary-examples",
        action="store_true",
        help="Run pressure-boundary GRC9V3 evidence examples.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.complex_hybrid_examples and args.pressure_boundary_examples:
        parser.error("--complex-hybrid-examples and --pressure-boundary-examples are exclusive")
    if args.pressure_boundary_examples:
        if args.refined_controls or args.appendix_e_pass_fail_controls:
            parser.error(
                "--pressure-boundary-examples cannot be combined with Iteration 5 flags"
            )
        session = run_grc9v3_pressure_boundary_session(
            session_id=args.session_id,
            session_root=args.session_root,
        )
    elif args.complex_hybrid_examples:
        if args.refined_controls or args.appendix_e_pass_fail_controls:
            parser.error(
                "--complex-hybrid-examples cannot be combined with Iteration 5 flags"
            )
        session = run_grc9v3_complex_hybrid_session(
            session_id=args.session_id,
            session_root=args.session_root,
        )
    else:
        session = run_grc9v3_discovery_control_session(
            session_id=args.session_id,
            session_root=args.session_root,
            refined_controls=args.refined_controls,
            appendix_e_pass_fail_controls=args.appendix_e_pass_fail_controls,
        )
    print(json.dumps(session.to_mapping(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DISCOVERY_PROGRAM",
    "DISCOVERY_SESSION_ROOT",
    "GRC9V3_COMPLEX_HYBRID_STEP_COUNTS",
    "GRC9V3_DISCOVERY_LOW_STEP_COUNTS",
    "GRC9V3_PRESSURE_BOUNDARY_STEP_COUNTS",
    "GRC9V3DiscoveryLaneRun",
    "GRC9V3DiscoverySessionRun",
    "run_grc9v3_complex_hybrid_session",
    "run_grc9v3_discovery_control_session",
    "run_grc9v3_pressure_boundary_session",
]
