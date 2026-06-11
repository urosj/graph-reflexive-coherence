"""Replayable generated-seed runs for GRC9 phenomenology discovery."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.models import GRC9
from pygrc.models.grc_9_checkpoints import export_grc9_graph_checkpoint
from pygrc.telemetry import (
    GRC9LaneContext,
    GraphCheckpointArtifact,
    GraphCheckpointCaptureConfig,
    RunTelemetryIdentity,
    TelemetryCaptureConfig,
    build_run_id,
    build_telemetry_artifact_layout,
    capture_run_telemetry,
    grc9_event_family_extensions,
    grc9_run_summary_family_extensions,
    grc9_step_family_extensions,
)
from pygrc.telemetry._grc9_extensions import (
    _build_grc9_event_extension,
    _build_grc9_run_summary_extension,
    _build_grc9_step_extension,
    _capture_grc9_identity_fission_observation,
)

from .grc9_hypothesis_catalog import GRC9HypothesisCatalog, default_grc9_hypothesis_catalog
from .grc9_manifest import is_session_id
from .grc9_seed_generator import GRC9GeneratedSeed, generate_grc9_seed
from .grc9_seed_generator import (
    GRC9_COMPLEX_EVENT_STABILITY_NAMES,
    GRC9_CORRECTED_GROWTH_COMBO_NAMES,
    GRC9_CORRECTED_GROWTH_COMPLEX_NAMES,
    GRC9_CORRECTED_GROWTH_ELEMENTARY_NAMES,
    GRC9_LIFECYCLE_COMBO_NAMES,
    GRC9_LIFECYCLE_EMITTER_NAMES,
    GRC9_LIFECYCLE_EMITTER_PERTURBATION_NAMES,
    GRC9_TARGETED_DIAGNOSTIC_NAMES,
    generate_grc9_complex_event_stability_fixture,
    generate_grc9_corrected_growth_combo_fixture,
    generate_grc9_corrected_growth_complex_fixture,
    generate_grc9_corrected_growth_elementary_fixture,
    generate_grc9_lifecycle_combo,
    generate_grc9_lifecycle_emitter,
    generate_grc9_lifecycle_emitter_perturbation,
    generate_grc9_targeted_diagnostic_fixture,
)


GRC9_DISCOVERY_LOW_STEP_COUNTS: Mapping[str, int] = {
    "spark_precursor": 8,
    "expansion_module": 10,
    "column_reassignment": 10,
    "growth_pressure": 15,
    "row_tensor_regime": 5,
    "column_diagnostic_regime": 5,
    "coarse_profile_sparsity": 3,
    "budget_correction": 3,
    "quiescent_basin": 20,
    "transport_pathway": 8,
    "fission_candidate": 12,
}
GRC9_EMITTER_REPAIR_STEP_COUNTS: Mapping[str, int] = {
    "spark_column_proxy_emitter": 3,
    "spark_instability_emitter": 3,
    "spark_to_expansion_emitter": 5,
    "growth_pressure_emitter": 5,
    "post_expansion_fission_emitter": 6,
}
GRC9_EMITTER_PERTURBATION_STEP_COUNTS: Mapping[str, int] = {
    "spark_column_proxy_eps_pass": 3,
    "spark_column_proxy_eps_fail": 3,
    "spark_instability_tau_pass": 3,
    "spark_instability_tau_fail": 3,
    "spark_to_expansion_d_eff_low": 5,
    "spark_to_expansion_d_eff_high": 5,
    "growth_pressure_lambda_high": 5,
    "growth_pressure_lambda_low": 5,
    "post_expansion_fission_min_mass_pass": 6,
    "post_expansion_fission_min_mass_fail": 6,
}
GRC9_LIFECYCLE_COMBO_STEP_COUNTS: Mapping[str, int] = {
    "spark_growth_combo": 3,
    "dual_spark_combo": 3,
    "spark_fission_combo": 6,
    "growth_fission_combo": 6,
    "spark_growth_fission_combo": 6,
}
GRC9_TARGETED_DIAGNOSTIC_STEP_COUNTS: Mapping[str, int] = {
    "row_tensor_strong_anisotropy_control": 2,
    "row_tensor_flat_control": 2,
    "column_proxy_near_zero_control": 2,
    "column_proxy_nonzero_control": 2,
    "coarse_cache_populated_sparse_profile_control": 0,
    "coarse_cache_populated_dense_profile_control": 0,
    "budget_uniform_shift_trigger_control": 1,
    "budget_simplex_projection_trigger_control": 1,
    "transport_short_path_dominant_control": 2,
    "transport_long_path_dominant_control": 2,
}
GRC9_COMPLEX_EVENT_STABILITY_STEP_COUNTS: Mapping[str, int] = {
    "all_events_complex_control": 6,
    "all_events_complex_extra_leaf_perturbation_control": 6,
    "all_events_complex_coherence_jitter_perturbation_control": 6,
    "all_events_complex_soft_threshold_perturbation_control": 6,
    "all_events_complex_high_degree_perturbation_control": 6,
}
GRC9_CORRECTED_GROWTH_ELEMENTARY_STEP_COUNTS: Mapping[str, int] = {
    "front_capacity_growth_positive_control": 3,
    "front_capacity_growth_pressure_boundary_positive_control": 3,
    "front_capacity_growth_no_front_control": 3,
    "front_capacity_growth_zero_birth_control": 3,
    "front_capacity_growth_pressure_boundary_zero_pressure_control": 3,
    "front_capacity_growth_closed_front_control": 3,
}
GRC9_CORRECTED_GROWTH_COMBO_STEP_COUNTS: Mapping[str, int] = {
    "corrected_spark_growth_combo": 4,
    "corrected_spark_pressure_boundary_growth_combo": 4,
    "corrected_growth_fission_combo": 6,
    "corrected_spark_growth_fission_combo": 6,
}
GRC9_CORRECTED_GROWTH_COMPLEX_STEP_COUNTS: Mapping[str, int] = {
    "corrected_all_events_complex_control": 6,
    "corrected_all_events_complex_extra_leaf_perturbation_control": 6,
    "corrected_all_events_complex_coherence_jitter_perturbation_control": 6,
    "corrected_all_events_complex_soft_threshold_perturbation_control": 6,
    "corrected_all_events_complex_high_degree_perturbation_control": 6,
}

DISCOVERY_SESSION_ROOT = Path("outputs/grc9/phenomenology_discovery/sessions")
DISCOVERY_TRACK = "phenomenology_discovery"
DISCOVERY_PROGRAM = "grc9_phenomenology_discovery"
DISCOVERY_SOURCE_REFERENCE = "implementation/GRC9-PhenomenologyDiscovery-Plan.md"
TELEMETRY_CONTRACT_SOURCE = "implementation/Phase-T-GRC9-TelemetryContract.md"


@dataclass(frozen=True)
class GRC9DiscoveryLaneRun:
    seed: GRC9GeneratedSeed
    requested_steps: int
    run_id: str
    artifact_root: str
    step_count: int
    event_count: int
    event_counts_by_kind: Mapping[str, int]
    checkpoint_count: int
    final_observables: Mapping[str, Any]

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "seed_family": self.seed.seed_family,
            "seed_name": self.seed.seed_name,
            "control_role": self.seed.control_role,
            "lane_name": self.seed.lane_name,
            "profile": self.seed.profile,
            "requested_steps": self.requested_steps,
            "run_id": self.run_id,
            "artifact_root": self.artifact_root,
            "step_count": self.step_count,
            "event_count": self.event_count,
            "event_counts_by_kind": dict(self.event_counts_by_kind),
            "checkpoint_count": self.checkpoint_count,
            "final_observables": dict(self.final_observables),
        }


@dataclass(frozen=True)
class GRC9DiscoverySessionRun:
    session_id: str
    session_root: Path
    lanes: tuple[GRC9DiscoveryLaneRun, ...]
    iteration: str = "I05_generated_runs_and_telemetry_capture"

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "iteration": self.iteration,
            "lane_count": len(self.lanes),
            "total_steps": sum(lane.step_count for lane in self.lanes),
            "total_events": sum(lane.event_count for lane in self.lanes),
            "lanes": [lane.to_mapping() for lane in self.lanes],
        }


def run_grc9_discovery_control_session(
    *,
    session_id: str = "S0004",
    session_root: str | Path | None = None,
    step_counts: Mapping[str, int] | None = None,
    catalog: GRC9HypothesisCatalog | None = None,
    emitter_repair: bool = False,
    emitter_perturbation: bool = False,
    lifecycle_combo: bool = False,
    targeted_diagnostic: bool = False,
    complex_event_stability: bool = False,
    corrected_growth_elementary: bool = False,
    corrected_growth_combo: bool = False,
    corrected_growth_complex: bool = False,
) -> GRC9DiscoverySessionRun:
    """Run all scheduled generated control lanes with Phase T-GRC9 telemetry."""

    if not is_session_id(session_id):
        raise ValueError("session_id must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    lanes_root = root / "generated_lanes"
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    if corrected_growth_complex:
        default_step_counts = GRC9_CORRECTED_GROWTH_COMPLEX_STEP_COUNTS
    elif corrected_growth_combo:
        default_step_counts = GRC9_CORRECTED_GROWTH_COMBO_STEP_COUNTS
    elif corrected_growth_elementary:
        default_step_counts = GRC9_CORRECTED_GROWTH_ELEMENTARY_STEP_COUNTS
    elif complex_event_stability:
        default_step_counts = GRC9_COMPLEX_EVENT_STABILITY_STEP_COUNTS
    elif targeted_diagnostic:
        default_step_counts = GRC9_TARGETED_DIAGNOSTIC_STEP_COUNTS
    elif lifecycle_combo:
        default_step_counts = GRC9_LIFECYCLE_COMBO_STEP_COUNTS
    elif emitter_perturbation:
        default_step_counts = GRC9_EMITTER_PERTURBATION_STEP_COUNTS
    elif emitter_repair:
        default_step_counts = GRC9_EMITTER_REPAIR_STEP_COUNTS
    else:
        default_step_counts = GRC9_DISCOVERY_LOW_STEP_COUNTS
    resolved_step_counts = dict(
        default_step_counts
    )
    resolved_step_counts.update(dict(step_counts or {}))
    planned_lane_names = _planned_lane_names(
        complex_event_stability=complex_event_stability,
        corrected_growth_elementary=corrected_growth_elementary,
        corrected_growth_combo=corrected_growth_combo,
        corrected_growth_complex=corrected_growth_complex,
        targeted_diagnostic=targeted_diagnostic,
        lifecycle_combo=lifecycle_combo,
        emitter_perturbation=emitter_perturbation,
        emitter_repair=emitter_repair,
        catalog=catalog,
    )
    _validate_step_count_coverage(resolved_step_counts, planned_lane_names)

    lane_results: list[GRC9DiscoveryLaneRun] = []
    if corrected_growth_complex:
        for fixture_name in GRC9_CORRECTED_GROWTH_COMPLEX_NAMES:
            lane_results.append(
                _run_discovery_lane(
                    seed=generate_grc9_corrected_growth_complex_fixture(
                        fixture_name
                    ),
                    requested_steps=int(resolved_step_counts[fixture_name]),
                    session_root=root,
                    lanes_root=lanes_root,
                )
            )
    elif corrected_growth_combo:
        for fixture_name in GRC9_CORRECTED_GROWTH_COMBO_NAMES:
            lane_results.append(
                _run_discovery_lane(
                    seed=generate_grc9_corrected_growth_combo_fixture(
                        fixture_name
                    ),
                    requested_steps=int(resolved_step_counts[fixture_name]),
                    session_root=root,
                    lanes_root=lanes_root,
                )
            )
    elif corrected_growth_elementary:
        for fixture_name in GRC9_CORRECTED_GROWTH_ELEMENTARY_NAMES:
            lane_results.append(
                _run_discovery_lane(
                    seed=generate_grc9_corrected_growth_elementary_fixture(
                        fixture_name
                    ),
                    requested_steps=int(resolved_step_counts[fixture_name]),
                    session_root=root,
                    lanes_root=lanes_root,
                )
            )
    elif complex_event_stability:
        for fixture_name in GRC9_COMPLEX_EVENT_STABILITY_NAMES:
            lane_results.append(
                _run_discovery_lane(
                    seed=generate_grc9_complex_event_stability_fixture(fixture_name),
                    requested_steps=int(resolved_step_counts[fixture_name]),
                    session_root=root,
                    lanes_root=lanes_root,
                )
            )
    elif targeted_diagnostic:
        for fixture_name in GRC9_TARGETED_DIAGNOSTIC_NAMES:
            lane_results.append(
                _run_discovery_lane(
                    seed=generate_grc9_targeted_diagnostic_fixture(fixture_name),
                    requested_steps=int(resolved_step_counts[fixture_name]),
                    session_root=root,
                    lanes_root=lanes_root,
                )
            )
    elif lifecycle_combo:
        for combo_name in GRC9_LIFECYCLE_COMBO_NAMES:
            lane_results.append(
                _run_discovery_lane(
                    seed=generate_grc9_lifecycle_combo(combo_name),
                    requested_steps=int(resolved_step_counts[combo_name]),
                    session_root=root,
                    lanes_root=lanes_root,
                )
            )
    elif emitter_perturbation:
        for perturbation_name in GRC9_LIFECYCLE_EMITTER_PERTURBATION_NAMES:
            lane_results.append(
                _run_discovery_lane(
                    seed=generate_grc9_lifecycle_emitter_perturbation(
                        perturbation_name
                    ),
                    requested_steps=int(resolved_step_counts[perturbation_name]),
                    session_root=root,
                    lanes_root=lanes_root,
                )
            )
    elif emitter_repair:
        for emitter_name in GRC9_LIFECYCLE_EMITTER_NAMES:
            lane_results.append(
                _run_discovery_lane(
                    seed=generate_grc9_lifecycle_emitter(emitter_name),
                    requested_steps=int(resolved_step_counts[emitter_name]),
                    session_root=root,
                    lanes_root=lanes_root,
                )
            )
    else:
        catalog = catalog or default_grc9_hypothesis_catalog()
        for family in catalog.seed_families:
            if not family.scheduled_for_generation:
                continue
            requested_steps = int(resolved_step_counts[family.seed_family])
            for control in (*family.positive_controls, *family.negative_controls):
                seed = generate_grc9_seed(
                    family.seed_family,
                    control.control_role,
                    catalog=catalog,
                )
                lane_results.append(
                    _run_discovery_lane(
                        seed=seed,
                        requested_steps=requested_steps,
                        session_root=root,
                        lanes_root=lanes_root,
                    )
                )

    session = GRC9DiscoverySessionRun(
        session_id=session_id,
        session_root=root,
        lanes=tuple(lane_results),
        iteration=(
            "I06_3_complex_event_stability_probe"
            if complex_event_stability
            else (
                "I03_3_corrected_grc9_full_complex"
                if corrected_growth_complex
                else (
                    "I03_2_corrected_grc9_growth_combos"
                    if corrected_growth_combo
                    else (
                        "I03_1_elementary_corrected_grc9_growth"
                        if corrected_growth_elementary
                        else (
                            "I06_2_targeted_diagnostic_fixture_generation"
                            if targeted_diagnostic
                            else (
                                "I05_3_lifecycle_combo_examples"
                                if lifecycle_combo
                                else (
                                    "I05_2_lifecycle_emitter_perturbation_sweep"
                                    if emitter_perturbation
                                    else (
                                        "I05_1_theory_first_lifecycle_emitter_repair"
                                        if emitter_repair
                                        else "I05_generated_runs_and_telemetry_capture"
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
    )
    _write_json(reports_root / "run_report.json", session.to_mapping())
    _write_initial_results(reports_root / "initial_results.md", session)
    _write_json(
        root / "session_manifest.json",
        _session_manifest(
            session,
            emitter_repair=emitter_repair,
            emitter_perturbation=emitter_perturbation,
            lifecycle_combo=lifecycle_combo,
            targeted_diagnostic=targeted_diagnostic,
            complex_event_stability=complex_event_stability,
            corrected_growth_elementary=corrected_growth_elementary,
            corrected_growth_combo=corrected_growth_combo,
            corrected_growth_complex=corrected_growth_complex,
        ),
    )
    _write_readme(
        root,
        session,
        emitter_repair=emitter_repair,
        emitter_perturbation=emitter_perturbation,
        lifecycle_combo=lifecycle_combo,
        targeted_diagnostic=targeted_diagnostic,
        complex_event_stability=complex_event_stability,
        corrected_growth_elementary=corrected_growth_elementary,
        corrected_growth_combo=corrected_growth_combo,
        corrected_growth_complex=corrected_growth_complex,
    )
    return session


def _planned_lane_names(
    *,
    complex_event_stability: bool,
    targeted_diagnostic: bool,
    lifecycle_combo: bool,
    emitter_perturbation: bool,
    emitter_repair: bool,
    corrected_growth_elementary: bool,
    corrected_growth_combo: bool,
    corrected_growth_complex: bool,
    catalog: GRC9HypothesisCatalog | None,
) -> tuple[str, ...]:
    if corrected_growth_complex:
        return tuple(GRC9_CORRECTED_GROWTH_COMPLEX_NAMES)
    if corrected_growth_combo:
        return tuple(GRC9_CORRECTED_GROWTH_COMBO_NAMES)
    if corrected_growth_elementary:
        return tuple(GRC9_CORRECTED_GROWTH_ELEMENTARY_NAMES)
    if complex_event_stability:
        return tuple(GRC9_COMPLEX_EVENT_STABILITY_NAMES)
    if targeted_diagnostic:
        return tuple(GRC9_TARGETED_DIAGNOSTIC_NAMES)
    if lifecycle_combo:
        return tuple(GRC9_LIFECYCLE_COMBO_NAMES)
    if emitter_perturbation:
        return tuple(GRC9_LIFECYCLE_EMITTER_PERTURBATION_NAMES)
    if emitter_repair:
        return tuple(GRC9_LIFECYCLE_EMITTER_NAMES)
    active_catalog = catalog or default_grc9_hypothesis_catalog()
    return tuple(
        family.seed_family
        for family in active_catalog.seed_families
        if family.scheduled_for_generation
    )


def _validate_step_count_coverage(
    step_counts: Mapping[str, int],
    planned_lane_names: Sequence[str],
) -> None:
    missing = tuple(name for name in planned_lane_names if name not in step_counts)
    if missing:
        raise ValueError(
            "missing GRC9 discovery step counts for planned lanes: "
            + ", ".join(missing)
        )


def _run_discovery_lane(
    *,
    seed: GRC9GeneratedSeed,
    requested_steps: int,
    session_root: Path,
    lanes_root: Path,
) -> GRC9DiscoveryLaneRun:
    model = GRC9.from_state(
        state=dict(seed.state_payload),
        params=dict(seed.expected_runtime_config),
    )
    params = model.get_params()
    seed_path = f"generated/grc9/phenomenology_discovery/{seed.lane_name}"
    run_identity = _run_identity(
        params_identity=params.params_hash,
        seed=seed,
        seed_path=seed_path,
        requested_steps=requested_steps,
    )
    lane_context = GRC9LaneContext(
        source_reference=TELEMETRY_CONTRACT_SOURCE,
        seed_source_reference=DISCOVERY_SOURCE_REFERENCE,
        lane_name=seed.lane_name,
        role=seed.control_role,
    )
    checkpoint_config = GraphCheckpointCaptureConfig(
        include_initial=True,
        include_final=True,
        every_step=True,
        include_flow_overlays=True,
        storage_mode="per_checkpoint_files",
    )
    graph_checkpoints: list[GraphCheckpointArtifact] = [
        _export_checkpoint(
            model=model,
            identity=run_identity,
            checkpoint_id="step-00000000",
            checkpoint_label="initial",
            checkpoint_reason="initial",
            event_step_range={"start_step_inclusive": 0, "end_step_inclusive": 0},
            event_count_window=0,
            event_counts_by_kind_window={},
            include_flow_overlays=True,
        )
    ]
    initial_observables = dict(model.compute_observables())
    step_results: list[Any] = []
    step_family_extensions: list[Mapping[str, Mapping[str, Any]]] = []
    event_family_extensions_by_step: list[list[Mapping[str, Mapping[str, Any]]]] = []
    identity_fission_observations: list[Mapping[str, Any]] = []

    for _ in range(requested_steps):
        step_result = model.step()
        step_results.append(step_result)
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
        event_counts = Counter(event.kind for event in step_result.events)
        graph_checkpoints.append(
            _export_checkpoint(
                model=model,
                identity=run_identity,
                checkpoint_id=f"step-{step_result.step_index:08d}",
                checkpoint_label=(
                    "final"
                    if step_result.step_index == requested_steps
                    else "interval"
                ),
                checkpoint_reason=(
                    "final"
                    if step_result.step_index == requested_steps
                    else "every_step"
                ),
                event_step_range={
                    "start_step_inclusive": step_result.step_index,
                    "end_step_inclusive": step_result.step_index,
                },
                event_count_window=len(step_result.events),
                event_counts_by_kind_window=dict(sorted(event_counts.items())),
                include_flow_overlays=True,
            )
        )

    final_observables = dict(model.compute_observables())
    shared_extensions = {
        "discovery": {
            "program": DISCOVERY_PROGRAM,
            "track": DISCOVERY_TRACK,
            "session_id": session_root.name,
            "seed_family": seed.seed_family,
            "control_role": seed.control_role,
            "lane_name": seed.lane_name,
            "profile": seed.profile,
            "generator_version": seed.generator_version,
        }
    }
    summary_extensions = grc9_run_summary_family_extensions(
        _build_grc9_run_summary_extension(
            model,
            step_results,
            lane_context=lane_context,
            identity_fission_observations=identity_fission_observations,
        )
    )
    artifact_layout = build_telemetry_artifact_layout(
        seed.lane_name,
        root_dir=lanes_root,
    )
    telemetry = capture_run_telemetry(
        model_family="grc9",
        params_identity=params.params_hash,
        seed_name=seed.seed_name,
        seed_source_reference=DISCOVERY_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family=seed.profile,
        rng_seed=int(params.evolution.get("rng_seed", 0)),
        requested_steps=requested_steps,
        initial_observables=initial_observables,
        step_results=step_results,
        final_observables=final_observables,
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        family_extensions=shared_extensions,
        step_family_extensions=step_family_extensions,
        event_family_extensions_by_step=event_family_extensions_by_step,
        summary_family_extensions=summary_extensions,
        graph_checkpoints=graph_checkpoints,
        artifact_layout=artifact_layout,
        config=TelemetryCaptureConfig(
            root_dir=lanes_root,
            write_artifacts=True,
            graph_checkpoints=checkpoint_config,
        ),
    )
    event_counts_total = Counter(
        event.kind for step_result in step_results for event in step_result.events
    )
    assert telemetry.artifact_layout is not None
    return GRC9DiscoveryLaneRun(
        seed=seed,
        requested_steps=requested_steps,
        run_id=telemetry.identity.run_id,
        artifact_root=str(telemetry.artifact_layout.run_dir),
        step_count=len(telemetry.step_rows),
        event_count=len(telemetry.event_rows),
        event_counts_by_kind=dict(sorted(event_counts_total.items())),
        checkpoint_count=len(graph_checkpoints),
        final_observables=final_observables,
    )


def _run_identity(
    *,
    params_identity: str,
    seed: GRC9GeneratedSeed,
    seed_path: str,
    requested_steps: int,
) -> RunTelemetryIdentity:
    rng_seed = int(seed.expected_runtime_config["evolution"].get("rng_seed", 0))
    run_id = build_run_id(
        model_family="grc9",
        params_identity=params_identity,
        seed_name=seed.seed_name,
        seed_source_reference=DISCOVERY_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family=seed.profile,
        rng_seed=rng_seed,
        requested_steps=requested_steps,
        overrides=None,
    )
    return RunTelemetryIdentity(
        run_id=run_id,
        model_family="grc9",
        params_identity=params_identity,
        seed_name=seed.seed_name,
        seed_source_reference=DISCOVERY_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family=seed.profile,
        rng_seed=rng_seed,
        requested_steps=requested_steps,
    )


def _export_checkpoint(
    *,
    model: GRC9,
    identity: RunTelemetryIdentity,
    checkpoint_id: str,
    checkpoint_label: str,
    checkpoint_reason: str,
    event_step_range: Mapping[str, int],
    event_count_window: int,
    event_counts_by_kind_window: Mapping[str, int],
    include_flow_overlays: bool,
) -> GraphCheckpointArtifact:
    return export_grc9_graph_checkpoint(
        model,
        identity=identity,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        checkpoint_reason=checkpoint_reason,
        event_step_range=event_step_range,
        event_count_window=event_count_window,
        event_counts_by_kind_window=event_counts_by_kind_window,
        include_flow_overlays=include_flow_overlays,
    )


def _session_manifest(
    session: GRC9DiscoverySessionRun,
    *,
    emitter_repair: bool,
    emitter_perturbation: bool,
    lifecycle_combo: bool,
    targeted_diagnostic: bool,
    complex_event_stability: bool,
    corrected_growth_elementary: bool,
    corrected_growth_combo: bool,
    corrected_growth_complex: bool,
) -> Mapping[str, Any]:
    report_path = session.session_root / "reports" / "run_report.json"
    return {
        "session_id": session.session_id,
        "program": DISCOVERY_PROGRAM,
        "family": "grc9",
        "track": DISCOVERY_TRACK,
        "iteration": session.iteration,
        "session_kind": "generated_run",
        "phenomenon": (
            "complex all-event stability probe"
            if complex_event_stability
            else (
                "corrected full-complex front-capacity growth probe"
                if corrected_growth_complex
                else (
                    "elementary corrected front-capacity growth controls"
                    if corrected_growth_elementary
                    else (
                        "corrected front-capacity growth composition controls"
                        if corrected_growth_combo
                        else (
                            "targeted diagnostic selector fixtures"
                            if targeted_diagnostic
                            else (
                                "lifecycle combination examples"
                                if lifecycle_combo
                                else (
                                    "lifecycle emitter perturbation sweep"
                                    if emitter_perturbation
                                    else (
                                        "lifecycle emitter repair"
                                        if emitter_repair
                                        else "all scheduled testable hypotheses"
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
        "seed_family": (
            "complex all-event stability fixture families"
            if complex_event_stability
            else (
                "corrected full-complex front-capacity growth fixture families"
                if corrected_growth_complex
                else (
                    "corrected front-capacity growth fixture families"
                    if corrected_growth_elementary
                    else (
                        "corrected front-capacity growth composition families"
                        if corrected_growth_combo
                        else (
                            "targeted diagnostic fixture families"
                            if targeted_diagnostic
                            else (
                                "composed lifecycle example families"
                                if lifecycle_combo
                                else (
                                    "repaired emitter perturbation families"
                                    if emitter_perturbation
                                    else (
                                        "repaired emitter families"
                                        if emitter_repair
                                        else "all scheduled default families"
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
        "control_role": (
            "complex and perturbation controls"
            if complex_event_stability
            else (
                "corrected growth full-complex controls"
                if corrected_growth_complex
                else (
                    "corrected growth controls"
                    if corrected_growth_elementary
                    else (
                        "corrected growth combo controls"
                        if corrected_growth_combo
                        else (
                            "diagnostic controls"
                            if targeted_diagnostic
                            else (
                                "combo controls"
                                if lifecycle_combo
                                else (
                                    "predicate perturbation controls"
                                    if emitter_perturbation
                                    else (
                                        "positive emitter controls"
                                        if emitter_repair
                                        else "all scheduled controls"
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
        "status": "completed",
        "created_at": "2026-04-26",
        "git_revision": _git_revision(),
        "dirty_worktree": _dirty_worktree(),
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            "pygrc.discovery.grc9_discovery_runner --session-id "
            f"{session.session_id}"
            + (
                " --complex-event-stability"
                if complex_event_stability
                else (
                    " --corrected-growth-complex"
                    if corrected_growth_complex
                    else (
                        " --corrected-growth-elementary"
                        if corrected_growth_elementary
                        else (
                            " --corrected-growth-combo"
                            if corrected_growth_combo
                            else (
                                " --targeted-diagnostic"
                                if targeted_diagnostic
                                else (
                                    " --lifecycle-combo"
                                    if lifecycle_combo
                                    else (
                                        " --emitter-perturbation"
                                        if emitter_perturbation
                                        else (" --emitter-repair" if emitter_repair else "")
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
        "input_paths": [
            "src/pygrc/discovery/grc9_hypothesis_catalog.py",
            "src/pygrc/discovery/grc9_seed_generator.py",
        ],
        "output_paths": [
            str(report_path),
            str(session.session_root / "reports" / "initial_results.md"),
            str(session.session_root / "generated_lanes"),
        ],
        "telemetry_paths": [
            lane.artifact_root for lane in session.lanes
        ],
        "checkpoint_paths": [
            f"{lane.artifact_root}/telemetry/graph_checkpoints"
            for lane in session.lanes
        ],
        "visualization_paths": [],
        "prediction_summary": (
            "Complex all-event fixtures should retain spark, expansion, growth, "
            "and fission-summary signatures under small node and parameter perturbations."
            if complex_event_stability
            else (
                "Corrected full-complex fixtures should retain all-event evidence "
                "while limiting growth to declared front capacity."
                if corrected_growth_complex
                else (
                    "Targeted diagnostic fixtures should expose row/column, coarse/profile, "
                    "budget, and transport contrasts that were ambiguous in S0009."
                    if targeted_diagnostic
                    else (
                        "Corrected elementary growth controls should separate front-capacity "
                        "growth from no-front, zero-birth, and closed-front controls."
                        if corrected_growth_elementary
                        else (
                            "Corrected growth composition controls should retain spark, "
                            "growth, and fission evidence without legacy broad growth."
                            if corrected_growth_combo
                            else (
                                "Composed lifecycle examples should expose multiple GRC9 signatures "
                                "in the same replayable run for selector validation."
                                if lifecycle_combo
                                else (
                                    "Threshold perturbations around repaired emitters should preserve "
                                    "or suppress lifecycle signatures according to the changed predicate."
                                    if emitter_perturbation
                                    else (
                                        "Theory-first repaired emitters should expose spark, expansion, "
                                        "growth, and fission telemetry signatures."
                                        if emitter_repair
                                        else (
                                            "Low-step Iteration 5 controls should expose immediate spark, "
                                            "expansion, growth, tensor, column diagnostic, coarse, budget, "
                                            "transport, quiescent, and fission telemetry signatures."
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
        "observation_summary": (
            f"Ran {len(session.lanes)} generated control lanes for "
            f"{sum(lane.step_count for lane in session.lanes)} total steps "
            f"and captured {sum(lane.event_count for lane in session.lanes)} events."
        ),
        "replay_notes": (
            "Complex all-event stability fixtures; include this session when replaying selector validation."
            if complex_event_stability
            else (
                "Corrected full-complex GRC9 growth fixtures; compare against legacy broad-growth full-complex behavior."
                if corrected_growth_complex
                else (
                    "Targeted diagnostic fixtures; include this session when replaying selector validation."
                    if targeted_diagnostic
                    else (
                        "Corrected GRC9 growth fixtures; use this session for front-capacity provenance selectors."
                        if corrected_growth_elementary
                        else (
                            "Corrected GRC9 growth combo fixtures; compare against legacy broad-growth S0007/S0021 behavior."
                            if corrected_growth_combo
                            else (
                                "Lifecycle combination examples; use these as higher-complexity selector fixtures."
                                if lifecycle_combo
                                else (
                                    "Lifecycle emitter perturbation sweep; compare pass/fail variants against S0005."
                                    if emitter_perturbation
                                    else (
                                        "Theory-first lifecycle emitter repair run; compare against S0004 negative evidence."
                                        if emitter_repair
                                        else "Low-step smoke discovery run; extend selected lanes later if behavior is delayed."
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
    }


def _write_readme(
    root: Path,
    session: GRC9DiscoverySessionRun,
    *,
    emitter_repair: bool,
    emitter_perturbation: bool,
    lifecycle_combo: bool,
    targeted_diagnostic: bool,
    complex_event_stability: bool,
    corrected_growth_elementary: bool,
    corrected_growth_combo: bool,
    corrected_growth_complex: bool,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {session.session_id}. "
        + (
            "GRC9 Lifecycle Combination Examples"
            if lifecycle_combo
            else (
                "GRC9 Complex All-Event Stability Probe"
                if complex_event_stability
                else (
                    "GRC9 Corrected Full-Complex Growth Probe"
                    if corrected_growth_complex
                    else (
                        "GRC9 Targeted Diagnostic Fixtures"
                        if targeted_diagnostic
                        else (
                            "GRC9 Corrected Front-Capacity Growth Controls"
                            if corrected_growth_elementary
                            else (
                                "GRC9 Corrected Front-Capacity Growth Combos"
                                if corrected_growth_combo
                                else (
                                    "GRC9 Lifecycle Emitter Perturbation Sweep"
                                    if emitter_perturbation
                                    else (
                                        "GRC9 Theory-First Lifecycle Emitter Repair"
                                        if emitter_repair
                                        else "GRC9 Generated Control Runs"
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
        "",
        "Status: `completed`",
        "",
        (
            "This session runs composed GRC9 lifecycle examples for selector validation."
            if lifecycle_combo
            else (
                "This session runs one complex all-event GRC9 graph and small node/parameter perturbations."
                if complex_event_stability
                else (
                    "This session reruns full-complex GRC9 graphs under corrected front-capacity growth."
                    if corrected_growth_complex
                    else (
                        "This session runs targeted row/column, coarse/profile, budget, and transport diagnostic fixtures."
                        if targeted_diagnostic
                        else (
                            "This session runs elementary corrected GRC9 front-capacity growth controls."
                            if corrected_growth_elementary
                            else (
                                "This session runs corrected GRC9 growth composition controls."
                                if corrected_growth_combo
                                else (
                                    "This session runs predicate perturbations around repaired GRC9 lifecycle emitters."
                                    if emitter_perturbation
                                    else (
                                        "This session runs repaired theory-first GRC9 lifecycle emitters."
                                        if emitter_repair
                                        else "This session runs all scheduled generated GRC9 discovery control lanes "
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
        (
            ""
            if lifecycle_combo
            or complex_event_stability
            or targeted_diagnostic
            or corrected_growth_elementary
            or corrected_growth_combo
            or corrected_growth_complex
            or emitter_perturbation
            or emitter_repair
            else "with the low step counts chosen for Iteration 5."
        ),
        "",
        "Replay:",
        "",
        "```bash",
        f"PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id {session.session_id}"
        + (
            " --lifecycle-combo"
            if lifecycle_combo
            else (
                " --complex-event-stability"
                if complex_event_stability
                else (
                    " --corrected-growth-complex"
                    if corrected_growth_complex
                    else (
                        " --targeted-diagnostic"
                        if targeted_diagnostic
                        else (
                            " --corrected-growth-elementary"
                            if corrected_growth_elementary
                            else (
                                " --corrected-growth-combo"
                                if corrected_growth_combo
                                else (
                                    " --emitter-perturbation"
                                    if emitter_perturbation
                                    else (" --emitter-repair" if emitter_repair else "")
                                )
                            )
                        )
                    )
                )
            )
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


def _write_initial_results(path: Path, session: GRC9DiscoverySessionRun) -> None:
    eventful_lanes = [lane for lane in session.lanes if lane.event_count > 0]
    emitter_repair = session.iteration == "I05_1_theory_first_lifecycle_emitter_repair"
    emitter_perturbation = (
        session.iteration == "I05_2_lifecycle_emitter_perturbation_sweep"
    )
    lifecycle_combo = session.iteration == "I05_3_lifecycle_combo_examples"
    targeted_diagnostic = (
        session.iteration == "I06_2_targeted_diagnostic_fixture_generation"
    )
    complex_event_stability = (
        session.iteration == "I06_3_complex_event_stability_probe"
    )
    corrected_growth_elementary = (
        session.iteration == "I03_1_elementary_corrected_grc9_growth"
    )
    corrected_growth_combo = (
        session.iteration == "I03_2_corrected_grc9_growth_combos"
    )
    corrected_growth_complex = (
        session.iteration == "I03_3_corrected_grc9_full_complex"
    )
    lines = [
        f"# {session.session_id} Initial Results",
        "",
        "## Scope",
        "",
        f"- {len(session.lanes)} generated control lanes",
        f"- {sum(lane.step_count for lane in session.lanes)} total simulation steps",
        f"- {sum(lane.checkpoint_count for lane in session.lanes)} GRC9 graph checkpoints",
        "- Every lane captured `steps.jsonl`, `events.jsonl`, `run_summary.json`, and graph checkpoint index artifacts",
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
            lines.append(
                f"  - `{lane.seed.lane_name}`: {lane.event_counts_by_kind}"
            )
    else:
        lines.append("- Event kinds: none")
    lines.extend(
        [
            "",
            "## Initial Finding",
            "",
            (
                "The combination examples compose repaired lifecycle mechanisms into multi-surface runs for selector validation."
                if lifecycle_combo
                else (
                    "The complex stability probe tests whether one all-event graph retains lifecycle evidence under small node and parameter perturbations."
                    if complex_event_stability
                    else (
                        "The corrected full-complex probe tests all-event evidence under front-capacity growth."
                        if corrected_growth_complex
                        else (
                            "The targeted diagnostic fixtures expose row/column, coarse/profile, budget, and transport contrasts for selector validation."
                            if targeted_diagnostic
                            else (
                                "The corrected growth controls separate front-capacity growth from no-front, zero-birth, and closed-front controls."
                                if corrected_growth_elementary
                                else (
                                    "The corrected growth combos test front-capacity growth inside connected spark/growth/fission compositions."
                                    if corrected_growth_combo
                                    else (
                                        "The perturbation sweep tested whether repaired lifecycle emitters preserve or suppress events when their controlling predicates are moved across thresholds."
                                        if emitter_perturbation
                                        else (
                                            "The theory-first emitter repair produced the missing spark, expansion, and growth lifecycle events."
                                            if emitter_repair
                                            else "The low-step generated controls produced telemetry and graph checkpoints, but spark and expansion lifecycle events did not fire."
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ),
            (
                "These runs intentionally include event coexistence, repeated growth cascades, dual expansion, and fission-summary coexistence."
                if lifecycle_combo
                else (
                    "Each lane should be evaluated for spark, expansion, growth, and fission-summary evidence rather than isolated pairwise behavior."
                    if complex_event_stability
                    else (
                        "Growth should be exactly front-capacity bounded while preserving full-complex spark, expansion, and fission evidence."
                        if corrected_growth_complex
                        else (
                            "The coarse/profile fixtures are zero-step warm-cache captures because normal runtime steps invalidate the coarse cache by design."
                            if targeted_diagnostic
                            else (
                                "Only the positive control should emit a paper-facing growth event with front-capacity provenance."
                                if corrected_growth_elementary
                                else (
                                    "Growth should remain bounded to declared front capacity, with no legacy broad-growth cascade."
                                    if corrected_growth_combo
                                    else (
                                        "Compare pass/fail lane pairs against S0005 to identify which signatures are robust and which depend tightly on runtime thresholds."
                                        if emitter_perturbation
                                        else (
                                            "The post-expansion fission emitter produced confirmed fission telemetry in the run summary without unrelated growth events."
                                            if emitter_repair
                                            else "This is useful discovery evidence: the first generated structures are valid GRC9 graphs, but most are diagnostic probes rather than event-emitting structures under the current runtime dynamics."
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ),
            "",
            (
                "The next discovery step should use S0005, S0006, and the latest connected combo replay together: isolated emitters, threshold pairs, and composed examples."
                if lifecycle_combo
                else (
                    "The next discovery step should rerun selector validation with this session and inspect which perturbations remain full all-event candidates."
                    if complex_event_stability
                    else (
                        "The next discovery step should classify legacy broad-growth evidence against this corrected full-complex session."
                        if corrected_growth_complex
                        else (
                            "The next discovery step should rerun selector validation across S0004-S0010 and only add more examples for remaining selector failures."
                            if targeted_diagnostic
                            else (
                                "The next discovery step should rerun corrected GRC9 growth-bearing composition lanes."
                                if corrected_growth_elementary
                                else (
                                    "The next discovery step should rerun corrected full-complex growth-bearing lanes."
                                    if corrected_growth_combo
                                    else (
                                        "The next discovery step should promote stable pass/fail pairs into selector fixtures."
                                        if emitter_perturbation
                                        else (
                                            "The next discovery step should validate these event windows with selectors and then decide whether to add perturbation envelopes around the repaired emitters."
                                            if emitter_repair
                                            else "The next discovery step should inspect saved telemetry fields and checkpoints to separate true negative controls, seeds that need stronger graph preconditions, seeds that need longer runs, and seed families whose predicted signature is diagnostic rather than lifecycle event based."
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ),
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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


def _dirty_worktree() -> bool | None:
    try:
        result = subprocess.run(
            ("git", "status", "--short"),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return bool(result.stdout.strip())


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", default="S0004")
    parser.add_argument("--session-root", default=None)
    parser.add_argument("--full-json", action="store_true")
    parser.add_argument("--emitter-repair", action="store_true")
    parser.add_argument("--emitter-perturbation", action="store_true")
    parser.add_argument("--lifecycle-combo", action="store_true")
    parser.add_argument("--targeted-diagnostic", action="store_true")
    parser.add_argument("--complex-event-stability", action="store_true")
    parser.add_argument("--corrected-growth-elementary", action="store_true")
    parser.add_argument("--corrected-growth-combo", action="store_true")
    parser.add_argument("--corrected-growth-complex", action="store_true")
    args = parser.parse_args(argv)
    session = run_grc9_discovery_control_session(
        session_id=args.session_id,
        session_root=args.session_root,
        emitter_repair=args.emitter_repair,
        emitter_perturbation=args.emitter_perturbation,
        lifecycle_combo=args.lifecycle_combo,
        targeted_diagnostic=args.targeted_diagnostic,
        complex_event_stability=args.complex_event_stability,
        corrected_growth_elementary=args.corrected_growth_elementary,
        corrected_growth_combo=args.corrected_growth_combo,
        corrected_growth_complex=args.corrected_growth_complex,
    )
    payload = session.to_mapping()
    if args.full_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            {
                "session_id": session.session_id,
                "iteration": payload["iteration"],
                "lane_count": payload["lane_count"],
                "total_steps": payload["total_steps"],
                "total_events": payload["total_events"],
                "report_path": str(session.session_root / "reports" / "run_report.json"),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "GRC9_DISCOVERY_LOW_STEP_COUNTS",
    "GRC9_EMITTER_REPAIR_STEP_COUNTS",
    "GRC9_EMITTER_PERTURBATION_STEP_COUNTS",
    "GRC9_LIFECYCLE_COMBO_STEP_COUNTS",
    "GRC9_COMPLEX_EVENT_STABILITY_STEP_COUNTS",
    "GRC9_CORRECTED_GROWTH_ELEMENTARY_STEP_COUNTS",
    "GRC9_CORRECTED_GROWTH_COMBO_STEP_COUNTS",
    "GRC9_CORRECTED_GROWTH_COMPLEX_STEP_COUNTS",
    "GRC9DiscoveryLaneRun",
    "GRC9DiscoverySessionRun",
    "run_grc9_discovery_control_session",
]
