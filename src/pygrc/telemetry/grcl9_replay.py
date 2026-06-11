"""Replay GRCL-9 source fixtures through the GRC9 runtime and telemetry."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
import os
import random
import stat
import subprocess
from typing import Any

from pygrc.core import (
    GRCParams,
    canonical_json_dumps,
    canonicalize_json_value,
    export_port_topology,
)
from pygrc.models import GRC9
from pygrc.models.grc_9_grcl9_lowering import (
    GRCL9LoweringResult,
    lower_grcl9_source_to_grc9_state,
)
from pygrc.models.grc_9_grcl9_provenance import (
    GRCL9_LOWERING_MODE,
    GRCL9_PROJECTOR_REVISION,
)
from pygrc.models.grc_9_checkpoints import export_grc9_graph_checkpoint
from pygrc.models.grc_9_state import GRC9State
from pygrc.landscapes.extensions.grcl9 import (
    GRCL9_LANDSCAPE_EXAMPLE_NAMES,
    GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES,
    GRCL9_LANDSCAPE_SEED_EXAMPLE_NAMES,
    GRCL9_LOWERING_MANIFEST_VERSION,
    GRCL9_SOURCE_FIXTURE_NAMES,
    GRCL9ColumnProxyProfile,
    GRCL9ExpansionRefinementRegion,
    GRCL9GrowthLocus,
    GRCL9InstabilityProfile,
    GRCL9PostExpansionFissionGeometry,
    GRCL9SparkCandidateRegion,
    GRCL9SourceDocument,
    compile_default_grcl9_landscape_examples_to_sources,
    compile_default_grcl9_landscape_seed_examples_to_sources,
    compile_legacy_grcl9_growth_landscape_seed_examples_to_sources,
    grcl9_landscape_example_by_name,
    grcl9_landscape_seed_example_by_name,
    grcl9_landscape_seed_example_path_by_name,
    legacy_grcl9_growth_landscape_seed_example_by_name,
    legacy_grcl9_growth_landscape_seed_example_path_by_name,
    grcl9_source_fixture_by_name,
)
from pygrc.telemetry.io import build_telemetry_artifact_layout
from pygrc.telemetry.recorder import (
    GraphCheckpointCaptureConfig,
    TelemetryCaptureConfig,
    capture_run_telemetry,
)
from pygrc.telemetry.schema import GraphCheckpointArtifact, RunTelemetryIdentity, build_run_id
from pygrc.telemetry._grc9_extensions import (
    _build_grc9_event_extension,
    _build_grc9_run_summary_extension,
    _build_grc9_step_extension,
    _capture_grc9_identity_fission_observation,
)
from pygrc.telemetry.grc9_contract import (
    GRC9LaneContext,
    grc9_event_family_extensions,
    grc9_run_summary_family_extensions,
    grc9_step_family_extensions,
)

GRCL9_REPLAY_VERSION = "grcl9_lowering_replay_v1"
GRCL9_REPLAY_ROOT = Path("outputs") / "grcl9" / "lowering"
GRCL9_SOURCE_REFERENCE = "implementation/GRCL-9-LoweringManifest.md"
GRC9_TELEMETRY_SOURCE_REFERENCE = "implementation/Phase-T-GRC9-TelemetryContract.md"
DEFAULT_REPLAY_STEPS = 5
LEGACY_GROWTH_SOURCE_MODES = frozenset({"legacy_growth_landscape_seed_examples"})
_STRUCTURAL_PROBE_SELECTOR_IDS = frozenset(
    {
        "basin_merge_pressure_candidate",
        "fission_persistence_failed_candidate",
        "membrane_rupture_structural_probe",
        "saddle_pressure_structural_probe",
        "support_loss_pressure_candidate",
    }
)
_DISCOVERY_OUTCOME_SELECTOR_IDS = frozenset(
    {
        "runtime_collapse_like_ambiguous",
        "runtime_collapse_like_classification",
        "runtime_collapse_like_observed",
        "runtime_collapse_like_long_window",
        "structural_only",
    }
)


@dataclass(frozen=True)
class GRCL9ReplayLaneResult:
    """One replayed source fixture lane."""

    fixture_name: str
    manifest_entry_id: str
    run_id: str
    requested_steps: int
    artifact_root: str
    source_fixture_path: str
    lowered_state_path: str
    selector_report_path: str
    checkpoint_count: int
    event_count: int
    event_counts_by_kind: Mapping[str, int]
    selector_status: str
    growth_semantics_status: str
    growth_parent_eligibility_mode: str
    legacy_broad_growth_non_evidence: bool

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "fixture_name": self.fixture_name,
            "manifest_entry_id": self.manifest_entry_id,
            "run_id": self.run_id,
            "requested_steps": self.requested_steps,
            "artifact_root": self.artifact_root,
            "source_fixture_path": self.source_fixture_path,
            "lowered_state_path": self.lowered_state_path,
            "selector_report_path": self.selector_report_path,
            "checkpoint_count": self.checkpoint_count,
            "event_count": self.event_count,
            "event_counts_by_kind": dict(self.event_counts_by_kind),
            "selector_status": self.selector_status,
            "growth_semantics_status": self.growth_semantics_status,
            "growth_parent_eligibility_mode": self.growth_parent_eligibility_mode,
            "legacy_broad_growth_non_evidence": self.legacy_broad_growth_non_evidence,
        }


@dataclass(frozen=True)
class GRCL9ReplaySessionResult:
    """Replayable GRCL-9 lowering session result."""

    session_id: str
    session_root: Path
    lanes: tuple[GRCL9ReplayLaneResult, ...]
    session_manifest_path: Path
    replay_script_path: Path
    experimental_log_path: Path

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "session_root": str(self.session_root),
            "lane_count": len(self.lanes),
            "lanes": [lane.to_mapping() for lane in self.lanes],
            "session_manifest_path": str(self.session_manifest_path),
            "replay_script_path": str(self.replay_script_path),
            "experimental_log_path": str(self.experimental_log_path),
        }


def run_grcl9_lowering_replay_session(
    *,
    session_id: str = "S0001",
    output_root: str | Path = GRCL9_REPLAY_ROOT,
    fixture_names: Sequence[str] | None = None,
    requested_steps: int = DEFAULT_REPLAY_STEPS,
    requested_steps_by_fixture: Mapping[str, int] | None = None,
    source_mode: str = "fixtures",
    force_legacy_growth: bool = False,
) -> GRCL9ReplaySessionResult:
    """Run built-in GRCL-9 source fixtures through GRC9 telemetry replay."""

    if not session_id or not session_id.startswith("S"):
        raise ValueError("session_id must be an S-prefixed replay session id")
    if requested_steps <= 0:
        raise ValueError("requested_steps must be positive")
    if source_mode not in {
        "fixtures",
        "landscape_examples",
        "landscape_seed_examples",
        "legacy_growth_landscape_seed_examples",
    }:
        raise ValueError(
            "source_mode must be fixtures, landscape_examples, or "
            "landscape_seed_examples, or legacy_growth_landscape_seed_examples"
        )
    _require_force_legacy_growth(
        source_mode=source_mode,
        force_legacy_growth=force_legacy_growth,
        program="pygrc.telemetry.grcl9_replay",
    )

    root = Path(output_root)
    session_root = root / "sessions" / session_id
    lanes_root = session_root / "lanes"
    sources_root = session_root / "source_fixtures"
    examples_root = session_root / "grcl_landscape_examples"
    seeds_root = session_root / "grcl_landscape_seeds"
    lowered_root = session_root / "lowered_states"
    reports_root = session_root / "reports"
    output_dirs = (lanes_root, sources_root, lowered_root, reports_root)
    if source_mode in {
        "landscape_examples",
        "landscape_seed_examples",
        "legacy_growth_landscape_seed_examples",
    }:
        output_dirs = output_dirs + (examples_root,)
    if source_mode in {
        "landscape_seed_examples",
        "legacy_growth_landscape_seed_examples",
    }:
        output_dirs = output_dirs + (seeds_root,)
    for path in output_dirs:
        path.mkdir(parents=True, exist_ok=True)

    selected_fixture_names = tuple(
        fixture_names
        or (
            GRCL9_LANDSCAPE_EXAMPLE_NAMES
            if source_mode == "landscape_examples"
            else GRCL9_LANDSCAPE_SEED_EXAMPLE_NAMES
            if source_mode == "landscape_seed_examples"
            else GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES
            if source_mode == "legacy_growth_landscape_seed_examples"
            else GRCL9_SOURCE_FIXTURE_NAMES
        )
    )
    fixtures = _source_documents_for_mode(source_mode)
    missing = tuple(name for name in selected_fixture_names if name not in fixtures)
    if missing:
        raise ValueError("unknown GRCL-9 fixtures: " + ", ".join(missing))
    if source_mode in {
        "landscape_examples",
        "landscape_seed_examples",
        "legacy_growth_landscape_seed_examples",
    }:
        _write_landscape_examples(
            examples_root,
            selected_fixture_names,
            source_mode=source_mode,
        )
    if source_mode in {
        "landscape_seed_examples",
        "legacy_growth_landscape_seed_examples",
    }:
        _write_landscape_seeds(
            seeds_root,
            selected_fixture_names,
            source_mode=source_mode,
        )

    lanes: list[GRCL9ReplayLaneResult] = []
    for fixture_name in selected_fixture_names:
        source = fixtures[fixture_name]
        steps = int(
            requested_steps_by_fixture.get(fixture_name, requested_steps)
            if requested_steps_by_fixture is not None
            else requested_steps
        )
        lanes.append(
            _run_replay_lane(
                source=source,
                requested_steps=steps,
                session_id=session_id,
                lanes_root=lanes_root,
                sources_root=sources_root,
                lowered_root=lowered_root,
                reports_root=reports_root,
            )
        )

    session_manifest_path = session_root / "session_manifest.json"
    replay_script_path = session_root / "replay.sh"
    experimental_log_path = root / "ExperimentalLog.md"
    manifest = _session_manifest(
        session_id=session_id,
        session_root=session_root,
        lanes=tuple(lanes),
        replay_script_path=replay_script_path,
        source_mode=source_mode,
        force_legacy_growth=force_legacy_growth,
    )
    _write_json(session_manifest_path, manifest)
    _write_replay_script(
        replay_script_path,
        session_id=session_id,
        requested_steps=requested_steps,
        fixture_names=selected_fixture_names,
        source_mode=source_mode,
        force_legacy_growth=force_legacy_growth,
    )
    _write_experimental_log(
        experimental_log_path,
        session_id=session_id,
        session_root=session_root,
        lanes=tuple(lanes),
    )
    return GRCL9ReplaySessionResult(
        session_id=session_id,
        session_root=session_root,
        lanes=tuple(lanes),
        session_manifest_path=session_manifest_path,
        replay_script_path=replay_script_path,
        experimental_log_path=experimental_log_path,
    )


def _source_documents_for_mode(source_mode: str) -> Mapping[str, GRCL9SourceDocument]:
    if source_mode == "landscape_seed_examples":
        return {
            source.fixture_name: source
            for source in compile_default_grcl9_landscape_seed_examples_to_sources()
        }
    if source_mode == "legacy_growth_landscape_seed_examples":
        return {
            source.fixture_name: source
            for source in compile_legacy_grcl9_growth_landscape_seed_examples_to_sources()
        }
    if source_mode == "landscape_examples":
        return {
            source.fixture_name: source
            for source in compile_default_grcl9_landscape_examples_to_sources()
        }
    return grcl9_source_fixture_by_name()


def _require_force_legacy_growth(
    *,
    source_mode: str,
    force_legacy_growth: bool,
    program: str,
) -> None:
    if source_mode not in LEGACY_GROWTH_SOURCE_MODES:
        return
    if force_legacy_growth:
        return
    raise ValueError(
        f"{program} refuses legacy broad-growth source mode `{source_mode}`. "
        "Use --force-legacy-growth only to reproduce historical diagnostic "
        "artifacts; forced legacy-growth outputs are replay-only non-evidence."
    )


def _write_landscape_examples(
    root: Path,
    fixture_names: Sequence[str],
    *,
    source_mode: str,
) -> None:
    if source_mode == "legacy_growth_landscape_seed_examples":
        examples = legacy_grcl9_growth_landscape_seed_example_by_name()
    elif source_mode == "landscape_seed_examples":
        examples = grcl9_landscape_seed_example_by_name()
    else:
        examples = grcl9_landscape_example_by_name()
    for fixture_name in fixture_names:
        _write_json(root / f"{fixture_name}.json", examples[fixture_name].to_mapping())


def _write_landscape_seeds(
    root: Path,
    fixture_names: Sequence[str],
    *,
    source_mode: str,
) -> None:
    paths = (
        legacy_grcl9_growth_landscape_seed_example_path_by_name()
        if source_mode == "legacy_growth_landscape_seed_examples"
        else grcl9_landscape_seed_example_path_by_name()
    )
    for fixture_name in fixture_names:
        source = paths[fixture_name]
        _write_text(root / source.name, source.read_text(encoding="utf-8"))


def _run_replay_lane(
    *,
    source: GRCL9SourceDocument,
    requested_steps: int,
    session_id: str,
    lanes_root: Path,
    sources_root: Path,
    lowered_root: Path,
    reports_root: Path,
) -> GRCL9ReplayLaneResult:
    growth_metadata = _growth_replay_metadata_for_source(source)
    runtime_config = _runtime_config_for_source(source)
    params = GRC9.from_config(runtime_config).get_params()
    lowered = lower_grcl9_source_to_grc9_state(source, params=params)
    if lowered.state.rng_state is None:
        rng = random.Random(int(params.evolution.get("rng_seed", 0)))
        lowered.state.rng_state = rng.getstate()
    model = GRC9(params=params, state=lowered.state)
    seed_path = f"grcl9/lowering/source_fixtures/{source.fixture_name}.json"
    run_identity = _run_identity(
        params=params,
        source=source,
        seed_path=seed_path,
        requested_steps=requested_steps,
    )
    lane_context = GRC9LaneContext(
        source_reference=GRC9_TELEMETRY_SOURCE_REFERENCE,
        lane_name=source.fixture_name,
        role=_control_role_for_source(source),
        profile_name="grcl9_lowering_replay",
        seed_source_reference=GRCL9_SOURCE_REFERENCE,
        source_lowering_mode=GRCL9_LOWERING_MODE,
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
        )
    ]
    initial_observables = dict(model.compute_observables())
    step_results: list[Any] = []
    step_family_extensions: list[Mapping[str, Mapping[str, Any]]] = []
    event_family_extensions_by_step: list[list[Mapping[str, Mapping[str, Any]]]] = []
    fission_observations: list[Mapping[str, Any]] = []

    for _ in range(requested_steps):
        step_result = model.step()
        step_results.append(step_result)
        step_family_extensions.append(
            grc9_step_family_extensions(
                _build_grc9_step_extension(model, lane_context=lane_context)
            )
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
        fission_observations.append(_capture_grc9_identity_fission_observation(model))
        event_counts_window = Counter(event.kind for event in step_result.events)
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
                event_counts_by_kind_window=dict(sorted(event_counts_window.items())),
            )
        )

    final_observables = dict(model.compute_observables())
    summary_extensions = grc9_run_summary_family_extensions(
        _build_grc9_run_summary_extension(
            model,
            step_results,
            lane_context=lane_context,
            identity_fission_observations=fission_observations,
            identity_fission_persistence_delta=_fission_delta(source),
            identity_fission_min_basin_mass=_fission_min_basin_mass(source),
        )
    )
    shared_extensions = {
        "grcl9": {
            "replay_version": GRCL9_REPLAY_VERSION,
            "source_schema_version": source.source_schema_version,
            "lowering_manifest_version": GRCL9_LOWERING_MANIFEST_VERSION,
            "projector_revision": GRCL9_PROJECTOR_REVISION,
            "lowering_mode": GRCL9_LOWERING_MODE,
            "fixture_name": source.fixture_name,
            "manifest_entry_id": source.manifest_entry_id,
            "expected_selector_ids": list(source.expected_selector_ids),
            "source_construct_kinds": [
                construct.construct_kind for construct in source.constructs
            ],
            "growth_replay_metadata": growth_metadata,
            "growth_semantics_status": growth_metadata["growth_semantics_status"],
            "growth_parent_eligibility_mode": growth_metadata[
                "growth_parent_eligibility_mode"
            ],
            "growth_parent_capacity_sources": canonicalize_json_value(
                model.get_state().cached_quantities.get(
                    "grcl9_growth_parent_capacity_sources",
                    {},
                )
            ),
            "front_growth_eligible_ports": canonicalize_json_value(
                model.get_state().cached_quantities.get(
                    "grcl9_front_growth_eligible_ports",
                    {},
                )
            ),
            "legacy_broad_growth_non_evidence": growth_metadata[
                "legacy_broad_growth_non_evidence"
            ],
        }
    }
    artifact_layout = build_telemetry_artifact_layout(
        source.fixture_name,
        root_dir=lanes_root,
    )
    telemetry = capture_run_telemetry(
        model_family="grc9",
        params_identity=params.params_hash,
        seed_name=source.fixture_name,
        seed_source_reference=GRCL9_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family="grcl9_lowering_replay",
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
    source_path = sources_root / f"{source.fixture_name}.json"
    lowered_path = lowered_root / f"{source.fixture_name}.json"
    selector_report_path = reports_root / f"{source.fixture_name}_selector_report.json"
    _write_json(source_path, source.to_mapping())
    _write_json(lowered_path, _lowering_result_to_mapping(lowered, params=params))
    selector_report = _selector_report(
        source=source,
        telemetry=telemetry,
        final_state=model.get_state(),
    )
    _write_json(selector_report_path, selector_report)
    event_counts_total = Counter(
        event.kind for step_result in step_results for event in step_result.events
    )
    assert telemetry.artifact_layout is not None
    return GRCL9ReplayLaneResult(
        fixture_name=source.fixture_name,
        manifest_entry_id=source.manifest_entry_id,
        run_id=telemetry.identity.run_id,
        requested_steps=requested_steps,
        artifact_root=str(telemetry.artifact_layout.run_dir),
        source_fixture_path=str(source_path),
        lowered_state_path=str(lowered_path),
        selector_report_path=str(selector_report_path),
        checkpoint_count=len(graph_checkpoints),
        event_count=len(telemetry.event_rows),
        event_counts_by_kind=dict(sorted(event_counts_total.items())),
        selector_status=str(selector_report["status"]),
        growth_semantics_status=str(growth_metadata["growth_semantics_status"]),
        growth_parent_eligibility_mode=str(
            growth_metadata["growth_parent_eligibility_mode"]
        ),
        legacy_broad_growth_non_evidence=bool(
            growth_metadata["legacy_broad_growth_non_evidence"]
        ),
    )


def _runtime_config_for_source(source: GRCL9SourceDocument) -> Mapping[str, Any]:
    has_spark_construct = any(
        isinstance(construct, GRCL9SparkCandidateRegion)
        for construct in source.constructs
    )
    evolution: dict[str, Any] = {
        "alpha": 0.0,
        "beta": 0.0,
        "gamma": 0.0,
        "delta": 0.0,
        "kappa_c": 10.0,
        "eta": 1.0,
        "rng_seed": 0,
        "eps_spark": 0.5,
        "tau_instability": 999.0,
        "lambda_birth": 0.0,
        "alpha_seed": 0.25,
        "w_bond": 1.0,
        "identity_fission_persistence_delta": 3,
        "identity_fission_min_basin_mass": 0.0,
        "site_potential_selection": "quadratic",
        "site_potential_params": {"scale": 0.0, "mu": 0.0},
    }
    modes = {
        "frame_mode": "fixed_port_chart",
        "curvature_backend": "none",
        "boundary_mode": "prune",
        "expansion_distribution_mode": "equal",
        "edge_label_selection": "all",
        "growth_parent_eligibility": _growth_parent_eligibility_mode_for_source(source),
    }
    for construct in source.constructs:
        if isinstance(construct, GRCL9ColumnProxyProfile):
            raw_threshold = construct.conductance_profile.get("spark_threshold")
            if isinstance(raw_threshold, int | float):
                evolution["eps_spark"] = float(raw_threshold)
        elif isinstance(construct, GRCL9InstabilityProfile):
            evolution["tau_instability"] = float(construct.tau_instability)
            if not any(
                isinstance(candidate, GRCL9ColumnProxyProfile)
                for candidate in source.constructs
            ):
                evolution["eps_spark"] = 0.0
        elif isinstance(construct, GRCL9ExpansionRefinementRegion):
            evolution["D_eff_target"] = int(construct.target_effective_degree)
            evolution["expansion_distribution_weights"] = tuple(
                construct.coherence_transfer_ratios
            )
            modes["expansion_distribution_mode"] = construct.coherence_transfer_mode
        elif isinstance(construct, GRCL9GrowthLocus):
            raw_lambda_birth = float(construct.lambda_birth)
            pressure_class = str((construct.pressure_profile or {}).get("class", ""))
            evolution["lambda_birth"] = (
                raw_lambda_birth
                if raw_lambda_birth >= 1.0 or pressure_class in {"high", "controlled_high"}
                else 0.0
            )
            if not has_spark_construct:
                evolution["eps_spark"] = 0.0
        elif isinstance(construct, GRCL9PostExpansionFissionGeometry):
            if not has_spark_construct:
                evolution["eps_spark"] = 0.0
            evolution["identity_fission_persistence_delta"] = int(
                construct.identity_fission_persistence_delta
            )
            evolution["identity_fission_min_basin_mass"] = float(
                construct.identity_fission_min_basin_mass
            )
    return {
        "dt": 0.1,
        "evolution": evolution,
        "constitutive_semantic_modes": modes,
    }


def _growth_parent_eligibility_mode_for_source(source: GRCL9SourceDocument) -> str:
    metadata = _growth_replay_metadata_for_source(source)
    return str(metadata["growth_parent_eligibility_mode"])


def _growth_replay_metadata_for_source(
    source: GRCL9SourceDocument,
) -> Mapping[str, Any]:
    growth_constructs = tuple(
        construct
        for construct in source.constructs
        if isinstance(construct, GRCL9GrowthLocus) and construct.executable
    )
    front_capacity_count = sum(
        1 for construct in growth_constructs if construct.growth_semantics == "front_capacity"
    )
    legacy_count = sum(
        1
        for construct in growth_constructs
        if construct.growth_semantics == "legacy_growth_locus"
    )
    if not growth_constructs:
        status = "none"
        if source.fixture_name.startswith("corrected_"):
            eligibility_mode = "grc9_front_capacity"
            evidence_status = "front_capacity_no_growth_control"
        else:
            eligibility_mode = "legacy_any_inactive_port"
            evidence_status = "non_growth_replay"
    elif legacy_count > 0:
        status = (
            "mixed_legacy_and_front_capacity"
            if front_capacity_count > 0
            else "legacy_growth_locus"
        )
        eligibility_mode = "legacy_any_inactive_port"
        evidence_status = "legacy_broad_growth_non_evidence"
    else:
        status = "front_capacity"
        eligibility_mode = "grc9_front_capacity"
        evidence_status = "front_capacity_growth_candidate"
    return {
        "growth_semantics_status": status,
        "growth_parent_eligibility_mode": eligibility_mode,
        "growth_evidence_status": evidence_status,
        "growth_construct_count": len(growth_constructs),
        "front_capacity_construct_count": front_capacity_count,
        "legacy_growth_construct_count": legacy_count,
        "legacy_broad_growth_non_evidence": evidence_status
        == "legacy_broad_growth_non_evidence",
    }


def _selector_report(
    *,
    source: GRCL9SourceDocument,
    telemetry: Any,
    final_state: GRC9State,
) -> Mapping[str, Any]:
    summary_grc9 = telemetry.run_summary.family_extensions["grc9"]
    lifecycle = summary_grc9.get("lifecycle_event_counts", {})
    expansion_summary = summary_grc9.get("expansion_summary", {})
    results = []
    for selector_id in source.expected_selector_ids:
        observed = _selector_value(
            selector_id=selector_id,
            source=source,
            lifecycle=lifecycle,
            expansion_summary=expansion_summary,
            final_state=final_state,
        )
        expected_pass = _expected_selector_pass(source, selector_id)
        passed = _selector_passed(selector_id, observed, expected_pass=expected_pass)
        results.append(
            {
                "selector_id": selector_id,
                "expected_pass": expected_pass,
                "observed_value": observed,
                "passed": passed,
                "telemetry_path": _selector_path(selector_id),
                "evidence_status": _selector_evidence_status(selector_id),
            }
        )
    all_passed = all(bool(result["passed"]) for result in results)
    status = "passed" if all_passed else "missed"
    return {
        "replay_version": GRCL9_REPLAY_VERSION,
        "fixture_name": source.fixture_name,
        "manifest_entry_id": source.manifest_entry_id,
        "status": status,
        "selector_results": results,
        "failure_notes": [
            (
                f"{result['selector_id']} expected "
                f"{'pass' if result['expected_pass'] else 'fail'} but observed "
                f"{result['observed_value']!r}"
            )
            for result in results
            if not result["passed"]
        ],
    }


def _expected_selector_pass(source: GRCL9SourceDocument, selector_id: str) -> bool:
    if selector_id in _STRUCTURAL_PROBE_SELECTOR_IDS | _DISCOVERY_OUTCOME_SELECTOR_IDS:
        return True
    if (
        selector_id == "expansion_module_size"
        and source.fixture_name.startswith("spark_to_expansion_d_eff_")
    ):
        return True
    if source.fixture_name.endswith(("_fail", "_low")):
        return False
    if source.fixture_name.endswith(("_pass", "_high")):
        return True
    if selector_id == "spark_column_proxy_count":
        return any(isinstance(construct, GRCL9ColumnProxyProfile) for construct in source.constructs)
    if selector_id == "spark_instability_count":
        return any(isinstance(construct, GRCL9InstabilityProfile) for construct in source.constructs)
    if selector_id == "growth_count":
        return any(isinstance(construct, GRCL9GrowthLocus) for construct in source.constructs)
    if selector_id == "pressure_boundary_growth_provenance":
        return any(
            isinstance(construct, GRCL9GrowthLocus)
            and construct.growth_semantics == "front_capacity"
            and construct.front_capacity_source == "pressure_boundary"
            for construct in source.constructs
        )
    if selector_id == "runtime_expansion_count":
        return any(
            isinstance(construct, GRCL9ExpansionRefinementRegion)
            for construct in source.constructs
        )
    if selector_id == "expansion_module_size":
        return any(
            isinstance(construct, GRCL9ExpansionRefinementRegion)
            for construct in source.constructs
        )
    if selector_id == "fission_confirmed_count":
        return any(
            isinstance(construct, GRCL9PostExpansionFissionGeometry)
            for construct in source.constructs
        )
    return False


def _selector_value(
    *,
    selector_id: str,
    source: GRCL9SourceDocument,
    lifecycle: Mapping[str, Any],
    expansion_summary: Mapping[str, Any],
    final_state: GRC9State,
) -> Any:
    if selector_id == "spark_column_proxy_count":
        return int(lifecycle.get("spark_column_proxy_count", 0))
    if selector_id == "spark_instability_count":
        return int(lifecycle.get("spark_instability_count", 0))
    if selector_id == "growth_count":
        return int(lifecycle.get("growth_count", 0))
    if selector_id == "pressure_boundary_growth_provenance":
        summary = final_state.cached_quantities.get("grcl9_growth_parent_capacity_sources", {})
        has_pressure_source = (
            isinstance(summary, Mapping)
            and any(
                isinstance(record, Mapping)
                and record.get("front_capacity_source") == "pressure_boundary"
                for record in summary.values()
            )
        )
        return int(lifecycle.get("growth_count", 0)) if has_pressure_source else 0
    if selector_id == "runtime_expansion_count":
        return int(lifecycle.get("expansion_count", 0))
    if selector_id == "fission_confirmed_count":
        return int(expansion_summary.get("identity_fission_confirmed_count", 0))
    if selector_id == "expansion_module_size":
        sizes = expansion_summary.get("module_size_distribution", [])
        if isinstance(sizes, Sequence) and not isinstance(sizes, str) and sizes:
            return max((int(size) for size in sizes), default=0)
        return int(expansion_summary.get("max_module_node_count", 0))
        return 0
    if selector_id == "lowered_bridge_edge_count":
        return len(final_state.cached_quantities.get("grcl9_bridge_edge_ids", ()))
    if selector_id == "fission_persistence_failed_candidate":
        candidate_count = int(expansion_summary.get("identity_fission_candidate_count", 0))
        confirmed_count = int(expansion_summary.get("identity_fission_confirmed_count", 0))
        return {
            "candidate_count": candidate_count,
            "confirmed_count": confirmed_count,
            "failed_persistence_candidate": candidate_count > 0 and confirmed_count == 0,
            "fission_persistence_failed_candidate": (
                candidate_count > 0 and confirmed_count == 0
            ),
        }
    if selector_id == "basin_merge_pressure_candidate":
        sink_count = len(final_state.sink_set)
        basin_count = len(final_state.basins)
        max_basin_size = max((len(nodes) for nodes in final_state.basins.values()), default=0)
        bridge_count = len(final_state.cached_quantities.get("grcl9_bridge_edge_ids", ()))
        confirmed_count = int(expansion_summary.get("identity_fission_confirmed_count", 0))
        return {
            "sink_count": sink_count,
            "basin_count": basin_count,
            "max_basin_size": max_basin_size,
            "bridge_edge_count": bridge_count,
            "confirmed_count": confirmed_count,
            "basin_merge_pressure_candidate": (
                sink_count >= 2 and basin_count >= 2 and bridge_count > 0 and confirmed_count == 0
            ),
        }
    if selector_id == "support_loss_pressure_candidate":
        conductances = [float(edge.conductance) for edge in final_state.port_edges.values()]
        min_conductance = min(conductances, default=0.0)
        construct_kinds = _source_construct_kinds(final_state) | {
            construct.construct_kind for construct in source.constructs
        }
        pressure_classes = _source_growth_pressure_classes(source)
        return {
            "min_conductance": min_conductance,
            "pressure_classes": sorted(pressure_classes),
            "source_construct_kinds": sorted(construct_kinds),
            "support_loss_pressure_candidate": (
                "growth_locus" in construct_kinds
                and (
                    0.0 < min_conductance <= 0.25
                    or any("support_loss" in pressure_class for pressure_class in pressure_classes)
                )
            ),
        }
    if selector_id == "membrane_rupture_structural_probe":
        term_payloads = _source_term_payloads(source)
        has_membrane = any(
            str(term.get("boundary_gradient_profile", {}).get("ridge_role", ""))
            == "rupture_prone_membrane"
            for term in term_payloads
            if isinstance(term, Mapping)
        )
        construct_kinds = _source_construct_kinds(final_state) | {
            construct.construct_kind for construct in source.constructs
        }
        saturated_ids = final_state.cached_quantities.get("grcl9_expected_saturated_node_ids", ())
        return {
            "has_membrane_source_term": has_membrane,
            "source_construct_kinds": sorted(construct_kinds),
            "expected_saturated_node_count": len(tuple(saturated_ids)),
            "membrane_rupture_structural_probe": (
                has_membrane
                and "spark_candidate_region" in construct_kinds
            ),
        }
    if selector_id == "saddle_pressure_structural_probe":
        term_payloads = _source_term_payloads(source)
        has_saddle = any(
            str(term.get("term_kind", "")) == "saddle_bridge"
            for term in term_payloads
            if isinstance(term, Mapping)
        )
        construct_kinds = _source_construct_kinds(final_state) | {
            construct.construct_kind for construct in source.constructs
        }
        saturated_ids = final_state.cached_quantities.get("grcl9_expected_saturated_node_ids", ())
        return {
            "has_saddle_source_term": has_saddle,
            "source_construct_kinds": sorted(construct_kinds),
            "expected_saturated_node_count": len(tuple(saturated_ids)),
            "saddle_pressure_structural_probe": (
                has_saddle
                and "instability_profile" in construct_kinds
            ),
        }
    if selector_id in _DISCOVERY_OUTCOME_SELECTOR_IDS:
        observation = _collapse_like_observation(
            source=source,
            final_state=final_state,
            expansion_summary=expansion_summary,
        )
        expected_classification = (
            "runtime_collapse_like_observed"
            if selector_id == "runtime_collapse_like_long_window"
            else selector_id
        )
        if selector_id == "runtime_collapse_like_ambiguous":
            expected_classification = "ambiguous"
        if selector_id == "runtime_collapse_like_classification":
            observation[selector_id] = observation["classification"] in {
                "ambiguous",
                "runtime_collapse_like_observed",
                "structural_only",
            }
            return observation
        observation[selector_id] = observation["classification"] == expected_classification
        return observation
    return None


def _selector_passed(
    selector_id: str,
    observed: Any,
    *,
    expected_pass: bool,
) -> bool:
    if selector_id == "expansion_module_size":
        observed_pass = isinstance(observed, int) and observed > 0
    elif selector_id == "runtime_expansion_count":
        observed_pass = isinstance(observed, int) and observed > 0
    elif selector_id in _STRUCTURAL_PROBE_SELECTOR_IDS | _DISCOVERY_OUTCOME_SELECTOR_IDS:
        observed_pass = (
            isinstance(observed, Mapping)
            and bool(observed.get(selector_id, False))
        )
    else:
        observed_pass = isinstance(observed, int) and observed > 0
    return observed_pass is expected_pass


def _selector_path(selector_id: str) -> str:
    paths = {
        "spark_column_proxy_count": (
            "family_extensions.grc9.lifecycle_event_counts.spark_column_proxy_count"
        ),
        "spark_instability_count": (
            "family_extensions.grc9.lifecycle_event_counts.spark_instability_count"
        ),
        "growth_count": "family_extensions.grc9.lifecycle_event_counts.growth_count",
        "pressure_boundary_growth_provenance": (
            "family_extensions.grc9.growth_summary.pressure_boundary_growth_count"
        ),
        "runtime_expansion_count": (
            "family_extensions.grc9.lifecycle_event_counts.expansion_count"
        ),
        "fission_confirmed_count": (
            "family_extensions.grc9.expansion_summary.identity_fission_confirmed_count"
        ),
        "expansion_module_size": (
            "family_extensions.grc9.expansion_summary.module_size_distribution"
        ),
        "fission_persistence_failed_candidate": (
            "family_extensions.grc9.expansion_summary.identity_fission_candidate_count"
            " + identity_fission_confirmed_count"
        ),
        "basin_merge_pressure_candidate": (
            "family_extensions.grc9.final_identity_summary.sink_count"
            " + graph_checkpoints.port_graph.basin_overlay"
        ),
        "support_loss_pressure_candidate": (
            "family_extensions.grc9.final_transport_summary.conductance_min"
            " + graph_checkpoints.port_graph.edge_records"
        ),
        "membrane_rupture_structural_probe": (
            "graph_checkpoints.port_graph.payload.grcl9_source_construct_kind"
            " + source_fixtures.compiled_source_provenance"
        ),
        "saddle_pressure_structural_probe": (
            "graph_checkpoints.port_graph.payload.grcl9_source_construct_kind"
            " + source_fixtures.compiled_source_provenance"
        ),
        "runtime_collapse_like_observed": (
            "family_extensions.grc9.final_identity_summary.sink_count"
            " + graph_checkpoints.port_graph.sink_overlay"
            " + grcl9_provenance.motif_role"
        ),
        "runtime_collapse_like_ambiguous": (
            "family_extensions.grc9.final_identity_summary.sink_count"
            " + graph_checkpoints.port_graph.sink_overlay"
            " + grcl9_provenance.motif_role"
            " + source_terms.stable_basin.selection_policy"
        ),
        "runtime_collapse_like_classification": (
            "family_extensions.grc9.final_identity_summary.sink_count"
            " + graph_checkpoints.port_graph.sink_overlay"
            " + grcl9_provenance.motif_role"
            " + source_terms.stable_basin.selection_policy"
        ),
        "runtime_collapse_like_long_window": (
            "family_extensions.grc9.final_identity_summary.sink_count"
            " + graph_checkpoints.port_graph.sink_overlay"
            " + grcl9_provenance.motif_role"
            " + source_terms.stable_basin.selection_policy"
        ),
        "structural_only": (
            "family_extensions.grc9.final_identity_summary.sink_count"
            " + graph_checkpoints.port_graph.sink_overlay"
            " + grcl9_provenance.motif_role"
        ),
    }
    return paths.get(selector_id, "unknown")


def _selector_evidence_status(selector_id: str) -> str:
    if selector_id == "fission_persistence_failed_candidate":
        return "artifact_backed"
    if selector_id in {
        "basin_merge_pressure_candidate",
        "membrane_rupture_structural_probe",
        "saddle_pressure_structural_probe",
        "support_loss_pressure_candidate",
    }:
        return "structural_only"
    if selector_id in {
        "runtime_collapse_like_observed",
        "runtime_collapse_like_ambiguous",
        "runtime_collapse_like_classification",
    }:
        return "runtime_diagnostic"
    if selector_id == "structural_only":
        return "runtime_negative_control"
    return "artifact_backed"


def _collapse_like_observation(
    *,
    source: GRCL9SourceDocument,
    final_state: GRC9State,
    expansion_summary: Mapping[str, Any],
) -> dict[str, Any]:
    source_declares_two_sinks = any(
        construct.construct_kind == "post_expansion_fission_geometry"
        for construct in source.constructs
    )
    role_by_node = _grcl9_motif_role_by_node(final_state)
    node_by_role = {role: node_id for node_id, role in role_by_node.items()}
    source_sink_roles = ("fission_sink_a", "fission_sink_b")
    stable_terms = _stable_basin_terms_by_id(source)
    use_developed_groups = any(
        int(term.get("support_node_count", 1)) > 1
        or str(term.get("selection_policy", "member_node")) == "group_centroid"
        for term in stable_terms.values()
    )
    source_sink_node_ids = [
        int(node_by_role[role])
        for role in source_sink_roles
        if role in node_by_role and final_state.topology.has_node(int(node_by_role[role]))
    ]
    group_a_node_ids = _source_basin_group_node_ids(
        role_by_node,
        sink_role="fission_sink_a",
        support_prefix="fission_support_a",
    )
    group_b_node_ids = _source_basin_group_node_ids(
        role_by_node,
        sink_role="fission_sink_b",
        support_prefix="fission_support_b",
    )
    final_sink_node_ids = sorted(int(node_id) for node_id in final_state.sink_set)
    if use_developed_groups:
        final_sink_roles = sorted(
            role_by_node.get(int(node_id), f"node_{node_id}")
            for node_id in final_sink_node_ids
            if int(node_id) in group_a_node_ids | group_b_node_ids
        )
        target_selected_node_id = _selected_basin_node_id(
            final_sink_node_ids=final_sink_node_ids,
            group_node_ids=group_a_node_ids,
            policy=str(
                stable_terms.get("sink_a", {}).get("selection_policy", "member_node")
            ),
        )
        lost_sink_roles = sorted(
            role
            for role in source_sink_roles
            if role in node_by_role and int(node_by_role[role]) not in final_state.sink_set
        )
        final_source_sink_count = sum(
            1
            for role in source_sink_roles
            if role in node_by_role and int(node_by_role[role]) in final_state.sink_set
        )
        live_source_sink_count = int(bool(group_a_node_ids)) + int(bool(group_b_node_ids))
    else:
        final_sink_roles = sorted(
            role_by_node.get(int(node_id), f"node_{node_id}")
            for node_id in final_sink_node_ids
            if int(node_id) in source_sink_node_ids
        )
        lost_sink_roles = sorted(
            role
            for role in source_sink_roles
            if role in node_by_role and int(node_by_role[role]) not in final_state.sink_set
        )
        live_source_sink_count = len(source_sink_node_ids)
        final_source_sink_count = len(final_sink_roles)
        target_selected_node_id = (
            int(node_by_role["fission_sink_a"])
            if "fission_sink_a" in node_by_role and int(node_by_role["fission_sink_a"]) in final_state.sink_set
            else None
        )
    classification = "ambiguous"
    if source_declares_two_sinks and live_source_sink_count >= 2:
        if (
            (
                final_source_sink_count == 1
                or (use_developed_groups and target_selected_node_id is not None)
            )
            and lost_sink_roles
            and (
                "fission_sink_b" in lost_sink_roles
                or "fission_sink_b_group" in lost_sink_roles
            )
        ):
            classification = "runtime_collapse_like_observed"
        elif final_source_sink_count >= 2 and not lost_sink_roles:
            classification = "structural_only"
        else:
            classification = "ambiguous"
    return {
        "classification": classification,
        "source_declares_two_sinks": source_declares_two_sinks,
        "source_sink_node_ids": source_sink_node_ids,
        "source_basin_a_node_ids": sorted(group_a_node_ids),
        "source_basin_b_node_ids": sorted(group_b_node_ids),
        "final_sink_node_ids": final_sink_node_ids,
        "final_source_sink_roles": final_sink_roles,
        "lost_source_sink_roles": lost_sink_roles,
        "target_selection_policy": str(
            stable_terms.get("sink_a", {}).get("selection_policy", "member_node")
        ),
        "target_selected_node_id": target_selected_node_id,
        "target_selection_kind": (
            "group_centroid"
            if str(stable_terms.get("sink_a", {}).get("selection_policy", "member_node"))
            == "group_centroid"
            else "member_node"
        ),
        "residual_collapsing_basin_sink_roles": sorted(
            role_by_node.get(int(node_id), f"node_{node_id}")
            for node_id in final_sink_node_ids
            if int(node_id) in group_b_node_ids
            and role_by_node.get(int(node_id)) != "fission_sink_b"
        ),
        "final_sink_count": len(final_state.sink_set),
        "final_basin_count": len(final_state.basins),
        "identity_fission_candidate_count": int(
            expansion_summary.get("identity_fission_candidate_count", 0)
        ),
        "identity_fission_confirmed_count": int(
            expansion_summary.get("identity_fission_confirmed_count", 0)
        ),
    }


def _stable_basin_terms_by_id(source: GRCL9SourceDocument) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for term in _source_term_payloads(source):
        if str(term.get("term_kind", "")) == "stable_basin":
            basin_id = term.get("basin_id")
            if basin_id is not None:
                result[str(basin_id)] = term
    return result


def _source_basin_group_node_ids(
    role_by_node: Mapping[int, str],
    *,
    sink_role: str,
    support_prefix: str,
) -> set[int]:
    return {
        int(node_id)
        for node_id, role in role_by_node.items()
        if role == sink_role or role.startswith(support_prefix)
    }


def _selected_basin_node_id(
    *,
    final_sink_node_ids: Sequence[int],
    group_node_ids: set[int],
    policy: str,
) -> int | None:
    candidates = sorted(set(int(node_id) for node_id in final_sink_node_ids) & group_node_ids)
    if not candidates:
        return None
    if policy == "group_centroid":
        return candidates[len(candidates) // 2]
    return candidates[0]


def _grcl9_motif_role_by_node(final_state: GRC9State) -> dict[int, str]:
    provenance = final_state.cached_quantities.get("grcl9_provenance", {})
    if not isinstance(provenance, Mapping):
        return {}
    nodes = provenance.get("nodes", {})
    if not isinstance(nodes, Mapping):
        return {}
    result: dict[int, str] = {}
    for raw_node_id, record in nodes.items():
        if not isinstance(record, Mapping):
            continue
        try:
            node_id = int(raw_node_id)
        except (TypeError, ValueError):
            continue
        role = record.get("motif_role")
        if role is not None:
            result[node_id] = str(role)
    return result


def _source_construct_kinds(final_state: GRC9State) -> set[str]:
    provenance = final_state.cached_quantities.get("grcl9_provenance", {})
    kinds: set[str] = set()
    if isinstance(provenance, Mapping):
        for collection_name in ("nodes", "edges"):
            collection = provenance.get(collection_name, {})
            if isinstance(collection, Mapping):
                for record in collection.values():
                    if isinstance(record, Mapping):
                        kind = record.get("source_construct_kind")
                        if kind is not None:
                            kinds.add(str(kind))
    return kinds


def _source_term_payloads(source: GRCL9SourceDocument) -> tuple[Mapping[str, Any], ...]:
    provenance = source.compiled_source_provenance or {}
    raw_terms = provenance.get("source_terms", ())
    if not isinstance(raw_terms, Sequence) or isinstance(raw_terms, str):
        return ()
    return tuple(item for item in raw_terms if isinstance(item, Mapping))


def _source_growth_pressure_classes(source: GRCL9SourceDocument) -> set[str]:
    classes: set[str] = set()
    for construct in source.constructs:
        if isinstance(construct, GRCL9GrowthLocus):
            raw_class = (construct.pressure_profile or {}).get("class")
            if raw_class is not None:
                classes.add(str(raw_class))
    return classes


def _lowering_result_to_mapping(
    result: GRCL9LoweringResult,
    *,
    params: GRCParams,
) -> Mapping[str, Any]:
    state = result.state
    return {
        "fixture_name": result.source.fixture_name,
        "manifest_entry_id": result.source.manifest_entry_id,
        "params_identity": params.params_hash,
        "topology": export_port_topology(state.topology),
        "node_coherence": {
            str(node_id): value for node_id, value in sorted(state.node_coherence.items())
        },
        "port_edges": {
            str(edge_id): {
                "node_u": edge.node_u,
                "port_u": edge.port_u,
                "node_v": edge.node_v,
                "port_v": edge.port_v,
                "conductance": edge.conductance,
                "flux_uv": edge.flux_uv,
            }
            for edge_id, edge in sorted(state.port_edges.items())
        },
        "geometric_length": {
            str(edge_id): value for edge_id, value in sorted(state.geometric_length.items())
        },
        "temporal_delay": {
            str(edge_id): value for edge_id, value in sorted(state.temporal_delay.items())
        },
        "flux_coupling": {
            str(edge_id): value for edge_id, value in sorted(state.flux_coupling.items())
        },
        "potential": {
            str(node_id): value for node_id, value in sorted(state.potential.items())
        },
        "sink_set": sorted(state.sink_set),
        "basins": {
            str(sink_id): sorted(nodes) for sink_id, nodes in sorted(state.basins.items())
        },
        "budget_target": state.budget_target,
        "cached_quantities": dict(state.cached_quantities),
        "node_id_by_role": dict(sorted(result.node_id_by_role.items())),
        "edge_id_by_role": dict(sorted(result.edge_id_by_role.items())),
    }


def _run_identity(
    *,
    params: GRCParams,
    source: GRCL9SourceDocument,
    seed_path: str,
    requested_steps: int,
) -> RunTelemetryIdentity:
    run_id = build_run_id(
        model_family="grc9",
        params_identity=params.params_hash,
        seed_name=source.fixture_name,
        seed_source_reference=GRCL9_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family="grcl9_lowering_replay",
        rng_seed=int(params.evolution.get("rng_seed", 0)),
        requested_steps=requested_steps,
        overrides=None,
    )
    return RunTelemetryIdentity(
        run_id=run_id,
        model_family="grc9",
        params_identity=params.params_hash,
        seed_name=source.fixture_name,
        seed_source_reference=GRCL9_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family="grcl9_lowering_replay",
        rng_seed=int(params.evolution.get("rng_seed", 0)),
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
        include_flow_overlays=True,
    )


def _control_role_for_source(source: GRCL9SourceDocument) -> str:
    if source.fixture_name.endswith("_pass"):
        return "pass_control"
    if source.fixture_name.endswith("_fail"):
        return "fail_control"
    if source.fixture_name.endswith("_high"):
        return "high_control"
    if source.fixture_name.endswith("_low"):
        return "low_control"
    return "control"


def _fission_delta(source: GRCL9SourceDocument) -> int | None:
    for construct in source.constructs:
        if isinstance(construct, GRCL9PostExpansionFissionGeometry):
            return int(construct.identity_fission_persistence_delta)
    return None


def _fission_min_basin_mass(source: GRCL9SourceDocument) -> float | None:
    for construct in source.constructs:
        if isinstance(construct, GRCL9PostExpansionFissionGeometry):
            return float(construct.identity_fission_min_basin_mass)
    return None


def _session_manifest(
    *,
    session_id: str,
    session_root: Path,
    lanes: Sequence[GRCL9ReplayLaneResult],
    replay_script_path: Path,
    source_mode: str,
    force_legacy_growth: bool,
) -> Mapping[str, Any]:
    input_paths = [
        "implementation/GRCL-9-LoweringManifest.md",
        "src/pygrc/landscapes/extensions/grcl9/fixtures.py",
        "src/pygrc/models/grc_9_grcl9_lowering.py",
        "src/pygrc/telemetry/grcl9_replay.py",
    ]
    if source_mode in {
        "landscape_examples",
        "landscape_seed_examples",
        "legacy_growth_landscape_seed_examples",
    }:
        input_paths.append("src/pygrc/landscapes/extensions/grcl9/examples.py")
    if source_mode == "landscape_seed_examples":
        input_paths.extend(
            str(path) for path in grcl9_landscape_seed_example_path_by_name().values()
        )
    if source_mode == "legacy_growth_landscape_seed_examples":
        input_paths.extend(
            str(path)
            for path in legacy_grcl9_growth_landscape_seed_example_path_by_name().values()
        )
    output_paths = [
        str(session_root / "source_fixtures"),
        str(session_root / "lowered_states"),
        str(session_root / "lanes"),
        str(session_root / "reports"),
    ]
    if source_mode in {
        "landscape_examples",
        "landscape_seed_examples",
        "legacy_growth_landscape_seed_examples",
    }:
        output_paths.insert(1, str(session_root / "grcl_landscape_examples"))
    if source_mode in {
        "landscape_seed_examples",
        "legacy_growth_landscape_seed_examples",
    }:
        output_paths.insert(1, str(session_root / "grcl_landscape_seeds"))
    return {
        "session_id": session_id,
        "program": "grcl9_lowering_replay",
        "family": "grcl9",
        "runtime_family": "grc9",
        "source_mode": source_mode,
        "force_legacy_growth": force_legacy_growth,
        "legacy_growth_guard": (
            "forced_replay_only_non_evidence"
            if source_mode in LEGACY_GROWTH_SOURCE_MODES and force_legacy_growth
            else "not_legacy_growth"
        ),
        "replay_version": GRCL9_REPLAY_VERSION,
        "lowering_manifest_version": GRCL9_LOWERING_MANIFEST_VERSION,
        "source_reference": GRCL9_SOURCE_REFERENCE,
        "telemetry_source_reference": GRC9_TELEMETRY_SOURCE_REFERENCE,
        "projector_revision": GRCL9_PROJECTOR_REVISION,
        "lowering_mode": GRCL9_LOWERING_MODE,
        "status": "completed",
        "created_at": "2026-04-25",
        "git_revision": _git_revision(),
        "dirty_worktree": _dirty_worktree(),
        "session_root": str(session_root),
        "replay_command": str(replay_script_path),
        "input_paths": input_paths,
        "output_paths": output_paths,
        "lanes": [lane.to_mapping() for lane in lanes],
        "summary": {
            "lane_count": len(lanes),
            "total_steps": sum(lane.requested_steps for lane in lanes),
            "total_events": sum(lane.event_count for lane in lanes),
            "selector_status_counts": dict(
                sorted(Counter(lane.selector_status for lane in lanes).items())
            ),
        },
    }


def _write_replay_script(
    path: Path,
    *,
    session_id: str,
    requested_steps: int,
    fixture_names: Sequence[str],
    source_mode: str,
    force_legacy_growth: bool,
) -> None:
    force_arg = " --force-legacy-growth" if force_legacy_growth else ""
    command = (
        "PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay "
        f"--session-id {session_id} --requested-steps {requested_steps} "
        f"--source-mode {source_mode}{force_arg} "
        + " ".join(f"--fixture {fixture_name}" for fixture_name in fixture_names)
    )
    payload = "#!/usr/bin/env bash\nset -euo pipefail\n" + command + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    current_mode = path.stat().st_mode
    os.chmod(path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _write_experimental_log(
    path: Path,
    *,
    session_id: str,
    session_root: Path,
    lanes: Sequence[GRCL9ReplayLaneResult],
) -> None:
    header = [
        "# GRCL-9 Lowering Experimental Log",
        "",
        "This log records replayable GRCL-9 source/lowering sessions.",
    ]
    section = [
        f"## {session_id}. Telemetry Replay",
        "",
        f"- Date: 2026-04-25",
        f"- Session root: `{session_root}`",
        f"- Replay version: `{GRCL9_REPLAY_VERSION}`",
        f"- Lanes: {len(lanes)}",
        f"- Total steps: {sum(lane.requested_steps for lane in lanes)}",
        f"- Total runtime events: {sum(lane.event_count for lane in lanes)}",
        "- Replay command: `./replay.sh` from the session directory",
        "",
        "| Fixture | Selectors | Events | Checkpoints |",
        "|---|---:|---:|---:|",
    ]
    for lane in lanes:
        section.append(
            f"| `{lane.fixture_name}` | `{lane.selector_status}` | "
            f"{lane.event_count} | {lane.checkpoint_count} |"
        )
    section.append("")
    if path.exists():
        existing = path.read_text(encoding="utf-8").rstrip()
        if f"## {session_id}. Telemetry Replay" in existing:
            _write_text(path, existing + "\n")
            return
        _write_text(path, existing + "\n\n" + "\n".join(section))
        return
    _write_text(path, "\n".join(header) + "\n\n" + "\n".join(section))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _write_text(path, canonical_json_dumps(canonicalize_json_value(payload)) + "\n")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _git_revision() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip()


def _dirty_worktree() -> bool | str:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return bool(result.stdout.strip())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", default="S0001")
    parser.add_argument("--output-root", default=str(GRCL9_REPLAY_ROOT))
    parser.add_argument("--requested-steps", type=int, default=DEFAULT_REPLAY_STEPS)
    parser.add_argument(
        "--fixture",
        action="append",
        dest="fixtures",
        help="Fixture name to include. May be passed multiple times.",
    )
    parser.add_argument(
        "--source-mode",
        choices=(
            "fixtures",
            "landscape_examples",
            "landscape_seed_examples",
            "legacy_growth_landscape_seed_examples",
        ),
        default="fixtures",
        help=(
            "Replay built-in mechanical fixtures, compiled GRCL landscape "
            "examples, seed-backed GRCL landscape examples, or quarantined "
            "legacy growth seed examples."
        ),
    )
    parser.add_argument(
        "--force-legacy-growth",
        action="store_true",
        help=(
            "Allow quarantined legacy broad-growth replay. Outputs remain "
            "diagnostic non-evidence."
        ),
    )
    args = parser.parse_args(argv)
    result = run_grcl9_lowering_replay_session(
        session_id=args.session_id,
        output_root=args.output_root,
        fixture_names=args.fixtures,
        requested_steps=args.requested_steps,
        source_mode=args.source_mode,
        force_legacy_growth=args.force_legacy_growth,
    )
    print(canonical_json_dumps(result.to_mapping()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_REPLAY_STEPS",
    "GRCL9_REPLAY_ROOT",
    "GRCL9_REPLAY_VERSION",
    "LEGACY_GROWTH_SOURCE_MODES",
    "GRCL9ReplayLaneResult",
    "GRCL9ReplaySessionResult",
    "run_grcl9_lowering_replay_session",
]
