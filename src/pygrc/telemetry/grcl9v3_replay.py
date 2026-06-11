"""Replay GRCL-9V3 source fixtures through the GRC9V3 runtime and telemetry."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
import json
from pathlib import Path
import stat
from typing import Any

from pygrc.core import (
    GRCParams,
    canonicalize_json_value,
    digest_snapshot,
    export_port_topology,
)
from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3_LANDSCAPE_EXAMPLE_NAMES,
    GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES,
    GRCL9V3_LOWERING_MANIFEST_VERSION,
    GRCL9V3_SOURCE_FIXTURE_NAMES,
    GRCL9V3AppendixEDivisionRegion,
    GRCL9V3ChoiceCollapseRegion,
    GRCL9V3ExpansionRefinementRegion,
    GRCL9V3GrowthLocus,
    GRCL9V3HybridSparkRegion,
    GRCL9V3SourceDocument,
    compile_default_grcl9v3_landscape_examples_to_sources,
    compile_default_grcl9v3_landscape_seed_examples_to_sources,
    compile_legacy_grcl9v3_growth_landscape_seed_examples_to_sources,
    grcl9v3_landscape_example_by_name,
    grcl9v3_landscape_seed_example_by_name,
    grcl9v3_landscape_seed_example_path_by_name,
    grcl9v3_source_fixture_by_name,
    legacy_grcl9v3_growth_landscape_seed_example_path_by_name,
)
from pygrc.models import (
    GRC9V3,
    GRCL9V3LoweringResult,
    GRCL9V3_LOWERING_MODE,
    GRCL9V3_PROJECTOR_REVISION,
    lower_grcl9v3_source_to_grc9v3_state,
)
from pygrc.models.grc_9_ports import port_to_rc
from pygrc.models.grc_9_state import PortEdge
from pygrc.models.grc_9_v3_state import GRC9V3NodeState, GRC9V3State
from pygrc.telemetry import (
    GRC9V3_TELEMETRY_CONTRACT_VERSION,
    GRC9V3LaneContext,
    GraphCheckpointArtifact,
    GraphCheckpointCaptureConfig,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    TelemetryCaptureConfig,
    build_run_id,
    capture_run_telemetry,
    grc9v3_event_family_extensions,
    grc9v3_run_summary_family_extensions,
    grc9v3_step_family_extensions,
)
from pygrc.telemetry._grc9v3_extensions import (
    _build_grc9v3_event_extension,
    _build_grc9v3_run_summary_extension,
    _build_grc9v3_step_extension,
)
from pygrc.telemetry.io import build_telemetry_artifact_layout


GRCL9V3_REPLAY_VERSION = "grcl9v3_lowering_replay_v1"
GRCL9V3_REPLAY_ROOT = Path("outputs") / "grcl9v3" / "lowering"
GRCL9V3_SOURCE_REFERENCE = "implementation/GRCL-9V3-ImplementationPlan.md"
GRC9V3_TELEMETRY_SOURCE_REFERENCE = "implementation/Phase-T-GRC9V3-TelemetryContract.md"
DEFAULT_REPLAY_STEPS = 3
HESSIAN_BACKEND_PROBE_REPORT = "hessian_backend_probe_report.json"
COLLAPSE_LEARNING_PROBE_REPORT = "collapse_learning_probe_report.json"
GROWTH_COLLAPSE_RELAY_PROBE_REPORT = "growth_collapse_relay_probe_report.json"
RELAY_PORT_PROBE_REPORT = "relay_port_probe_report.json"
_SOURCE_MODES = frozenset(
    {
        "collapse_learning_probe",
        "fixtures",
        "growth_collapse_relay_probe",
        "relay_port_probe",
        "landscape_examples",
        "landscape_seed_examples",
        "hessian_backend_probe",
        "legacy_growth_landscape_seed_examples",
        "pressure_boundary_probe",
    }
)
_HESSIAN_BACKEND_PROBE_BASES = (
    ("anisotropic_spark", "hybrid_spark_gate_positive_control"),
    ("expansion_gate", "spark_to_expansion_positive_control"),
    ("saddle_choice", "choice_collapse_positive_control"),
    ("transport_corridor", "transport_basin_rerouting_positive_control"),
    ("quiescent_isotropic", "quiescent_hybrid_control_no_event_control"),
)
_HESSIAN_BACKEND_PROBE_BACKENDS = (
    ("row_basis", "row_basis_diagonal", "hessian_row_basis_diagnostic"),
    (
        "weighted_least_squares",
        "weighted_least_squares",
        "hessian_weighted_least_squares_diagnostic",
    ),
)
_COLLAPSE_LEARNING_PROBE_SOURCE = "multi_center_delayed_collapse_learning"
_COLLAPSE_LEARNING_PROBE_LAMBDAS = (
    ("lambda_005", 0.05),
    ("lambda_010", 0.10),
    ("lambda_020", 0.20),
    ("lambda_040", 0.40),
)
_GROWTH_COLLAPSE_RELAY_PROBES = (
    ("lambda_020", 0.20),
)
_RELAY_PORT_PROBES = (
    (
        "support_040_alpha_035",
        {"lambda_birth": 0.20, "alpha_seed": 0.35, "w_bond": 1.0},
        {
            "geometry": "relay_port",
            "parent_coherence": 3.0,
            "support_coherence": 4.0,
            "support_conductance": 1.0,
            "support_flux": 0.75,
            "outlet_coherence": 0.25,
            "outlet_conductance": 0.12,
        },
    ),
    (
        "support_050_alpha_050",
        {"lambda_birth": 0.20, "alpha_seed": 0.50, "w_bond": 0.75},
        {
            "geometry": "relay_port",
            "parent_coherence": 3.0,
            "support_coherence": 5.0,
            "support_conductance": 1.1,
            "support_flux": 0.85,
            "outlet_coherence": 0.20,
            "outlet_conductance": 0.18,
        },
    ),
    (
        "support_060_alpha_060",
        {"lambda_birth": 0.25, "alpha_seed": 0.60, "w_bond": 0.60},
        {
            "geometry": "relay_port",
            "parent_coherence": 3.0,
            "support_coherence": 6.0,
            "support_conductance": 1.2,
            "support_flux": 1.0,
            "outlet_coherence": 0.15,
            "outlet_conductance": 0.22,
        },
    ),
)
_HESSIAN_DELTA_FIELDS = (
    "family_extensions.grc9v3.row_basis_differential.current_min_signed_hessian_min",
    "family_extensions.grc9v3.row_basis_differential.signed_hessian_min",
    "family_extensions.grc9v3.row_basis_differential.signed_hessian_max",
    "family_extensions.grc9v3.row_basis_differential.signed_hessian_mean",
    "family_extensions.grc9v3.hybrid_tensor.tensor_trace_mean",
    "family_extensions.grc9v3.hybrid_tensor.tensor_anisotropy_max",
    "family_extensions.grc9v3.hybrid_tensor.row_mismatch_sum_max",
    "family_extensions.grc9v3.hybrid_spark_state.last_candidate_min_signed_hessian",
)


@dataclass(frozen=True)
class GRCL9V3ReplayLaneResult:
    """One replayed GRCL-9V3 source fixture lane."""

    fixture_name: str
    manifest_entry_id: str
    run_id: str
    requested_steps: int
    artifact_root: str
    source_fixture_path: str
    lowered_state_path: str
    replay_report_path: str
    checkpoint_count: int
    event_count: int
    event_counts_by_kind: Mapping[str, int]
    replay_step_rows_match: bool
    replay_event_rows_match: bool
    replay_digest_match: bool

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "fixture_name": self.fixture_name,
            "manifest_entry_id": self.manifest_entry_id,
            "run_id": self.run_id,
            "requested_steps": self.requested_steps,
            "artifact_root": self.artifact_root,
            "source_fixture_path": self.source_fixture_path,
            "lowered_state_path": self.lowered_state_path,
            "replay_report_path": self.replay_report_path,
            "checkpoint_count": self.checkpoint_count,
            "event_count": self.event_count,
            "event_counts_by_kind": dict(self.event_counts_by_kind),
            "replay_step_rows_match": self.replay_step_rows_match,
            "replay_event_rows_match": self.replay_event_rows_match,
            "replay_digest_match": self.replay_digest_match,
        }


@dataclass(frozen=True)
class GRCL9V3ReplaySessionResult:
    """Replayable GRCL-9V3 lowering session result."""

    session_id: str
    session_root: Path
    lanes: tuple[GRCL9V3ReplayLaneResult, ...]
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


def run_grcl9v3_lowering_replay_session(
    *,
    session_id: str = "S0001",
    output_root: str | Path = GRCL9V3_REPLAY_ROOT,
    fixture_names: Sequence[str] | None = None,
    requested_steps: int = DEFAULT_REPLAY_STEPS,
    requested_steps_by_fixture: Mapping[str, int] | None = None,
    source_mode: str = "fixtures",
) -> GRCL9V3ReplaySessionResult:
    """Run built-in GRCL-9V3 source fixtures through GRC9V3 telemetry replay."""

    if not session_id or not session_id.startswith("S"):
        raise ValueError("session_id must be an S-prefixed replay session id")
    if requested_steps <= 0:
        raise ValueError("requested_steps must be positive")
    if source_mode not in _SOURCE_MODES:
        raise ValueError(
            "source_mode must be fixtures, landscape_examples, "
            "landscape_seed_examples, hessian_backend_probe, or "
            "collapse_learning_probe, growth_collapse_relay_probe, or "
            "relay_port_probe, pressure_boundary_probe, or "
            "legacy_growth_landscape_seed_examples"
        )

    root = Path(output_root)
    session_root = root / "sessions" / session_id
    lanes_root = session_root / "lanes"
    sources_root = session_root / "source_fixtures"
    examples_root = session_root / "grcl9v3_landscape_examples"
    seeds_root = session_root / "grcl9v3_landscape_seeds"
    lowered_root = session_root / "lowered_states"
    reports_root = session_root / "reports"
    output_dirs = (lanes_root, sources_root, lowered_root, reports_root)
    if source_mode in {"landscape_examples", "landscape_seed_examples"}:
        output_dirs = output_dirs + (examples_root,)
    if source_mode == "landscape_seed_examples":
        output_dirs = output_dirs + (seeds_root,)
    for path in output_dirs:
        path.mkdir(parents=True, exist_ok=True)

    selected_fixture_names = tuple(
        fixture_names
        or (
            tuple(_hessian_backend_probe_sources())
            if source_mode == "hessian_backend_probe"
            else tuple(_collapse_learning_probe_sources())
            if source_mode == "collapse_learning_probe"
            else tuple(_growth_collapse_relay_probe_sources())
            if source_mode == "growth_collapse_relay_probe"
            else tuple(_relay_port_probe_sources())
            if source_mode == "relay_port_probe"
            else
            GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES
            if source_mode == "landscape_seed_examples"
            else GRCL9V3_LANDSCAPE_EXAMPLE_NAMES
            if source_mode == "landscape_examples"
            else GRCL9V3_SOURCE_FIXTURE_NAMES
        )
    )
    fixtures = _source_documents_for_mode(source_mode)
    missing = tuple(name for name in selected_fixture_names if name not in fixtures)
    if missing:
        raise ValueError("unknown GRCL-9V3 fixtures: " + ", ".join(missing))
    if source_mode in {"landscape_examples", "landscape_seed_examples"}:
        _write_landscape_examples(
            examples_root,
            selected_fixture_names,
            source_mode=source_mode,
        )
    if source_mode == "landscape_seed_examples":
        _write_landscape_seeds(seeds_root, selected_fixture_names)

    lanes: list[GRCL9V3ReplayLaneResult] = []
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
    extra_report_paths: dict[str, str] = {}
    if source_mode == "hessian_backend_probe":
        report_path = reports_root / HESSIAN_BACKEND_PROBE_REPORT
        _write_json(report_path, _hessian_backend_probe_report(tuple(lanes)))
        extra_report_paths["hessian_backend_probe_report"] = str(report_path)
    if source_mode == "collapse_learning_probe":
        report_path = reports_root / COLLAPSE_LEARNING_PROBE_REPORT
        _write_json(report_path, _collapse_learning_probe_report(tuple(lanes)))
        extra_report_paths["collapse_learning_probe_report"] = str(report_path)
    if source_mode == "growth_collapse_relay_probe":
        report_path = reports_root / GROWTH_COLLAPSE_RELAY_PROBE_REPORT
        _write_json(report_path, _growth_collapse_relay_probe_report(tuple(lanes)))
        extra_report_paths["growth_collapse_relay_probe_report"] = str(report_path)
    if source_mode == "relay_port_probe":
        report_path = reports_root / RELAY_PORT_PROBE_REPORT
        _write_json(report_path, _relay_port_probe_report(tuple(lanes)))
        extra_report_paths["relay_port_probe_report"] = str(report_path)
    _write_json(
        session_manifest_path,
        _session_manifest(
            session_id=session_id,
            session_root=session_root,
            lanes=tuple(lanes),
            replay_script_path=replay_script_path,
            requested_steps=requested_steps,
            fixture_names=selected_fixture_names,
            source_mode=source_mode,
            extra_report_paths=extra_report_paths,
        ),
    )
    _write_replay_script(
        replay_script_path,
        session_id=session_id,
        requested_steps=requested_steps,
        fixture_names=selected_fixture_names,
        source_mode=source_mode,
    )
    _write_experimental_log(
        experimental_log_path,
        session_id=session_id,
        session_root=session_root,
        lanes=tuple(lanes),
    )
    return GRCL9V3ReplaySessionResult(
        session_id=session_id,
        session_root=session_root,
        lanes=tuple(lanes),
        session_manifest_path=session_manifest_path,
        replay_script_path=replay_script_path,
        experimental_log_path=experimental_log_path,
    )


def _source_documents_for_mode(source_mode: str) -> Mapping[str, GRCL9V3SourceDocument]:
    if source_mode == "hessian_backend_probe":
        return _hessian_backend_probe_sources()
    if source_mode == "collapse_learning_probe":
        return _collapse_learning_probe_sources()
    if source_mode == "growth_collapse_relay_probe":
        return _growth_collapse_relay_probe_sources()
    if source_mode == "relay_port_probe":
        return _relay_port_probe_sources()
    if source_mode == "pressure_boundary_probe":
        return _pressure_boundary_probe_sources()
    if source_mode == "landscape_seed_examples":
        return {
            source.fixture_name: source
            for source in compile_default_grcl9v3_landscape_seed_examples_to_sources()
        }
    if source_mode == "legacy_growth_landscape_seed_examples":
        return {
            source.fixture_name: source
            for source in compile_legacy_grcl9v3_growth_landscape_seed_examples_to_sources()
        }
    if source_mode == "landscape_examples":
        return {
            source.fixture_name: source
            for source in compile_default_grcl9v3_landscape_examples_to_sources()
        }
    return grcl9v3_source_fixture_by_name()


def _pressure_boundary_probe_sources() -> Mapping[str, GRCL9V3SourceDocument]:
    return {
        "pressure_boundary_growth_positive_control": GRCL9V3SourceDocument(
            fixture_name="pressure_boundary_growth_positive_control",
            manifest_entry_id="composed_grcl9v3_hybrid_composition_v1",
            expected_selector_ids=("pressure_boundary_growth_provenance",),
            constructs=(
                GRCL9V3GrowthLocus(
                    construct_id="pressure_boundary_growth",
                    motif_id="grc9v3-motif-s0006-growth-pressure-positive-control",
                    source_role="positive_control",
                    ownership="grc9_mechanical",
                    parent_region_id="pressure_parent",
                    inactive_parent_port=6,
                    outward_pressure_profile={
                        "pressure": "boundary_front",
                        "support_conductance": 2.0,
                        "support_flux": 2.0,
                    },
                    lambda_birth=1.0,
                    growth_semantics="front_capacity",
                    front_capacity_source="pressure_boundary",
                ),
            ),
            notes={
                "boundary": (
                    "pressure-boundary source-backed probe for the "
                    "PressureBoundary track"
                )
            },
            compiled_source_provenance={
                "composed_source_ancestry": ("pressure_boundary", "growth")
            },
        )
    }


def _collapse_learning_probe_sources() -> Mapping[str, GRCL9V3SourceDocument]:
    """Build lambda-birth timing probes over the delayed multi-center source."""

    base_sources = {
        source.fixture_name: source
        for source in (
            *compile_default_grcl9v3_landscape_seed_examples_to_sources(),
            *compile_legacy_grcl9v3_growth_landscape_seed_examples_to_sources(),
        )
    }
    base = base_sources[_COLLAPSE_LEARNING_PROBE_SOURCE]
    probes: dict[str, GRCL9V3SourceDocument] = {}
    for suffix, lambda_birth in _COLLAPSE_LEARNING_PROBE_LAMBDAS:
        fixture_name = f"collapse_learning_probe_{suffix}_control"
        notes = dict(base.notes or {})
        runtime_overrides = dict(notes.get("runtime_diagnostic_overrides", {}))
        runtime_overrides["lambda_birth"] = float(lambda_birth)
        notes.update(
            {
                "boundary": (
                    "runtime lambda_birth timing probe over the delayed "
                    "multi-center GRCL-9V3 source; this is not a new source "
                    "ontology term"
                ),
                "collapse_learning_probe_source_fixture": base.fixture_name,
                "collapse_learning_probe_lambda_birth": float(lambda_birth),
                "runtime_diagnostic_overrides": runtime_overrides,
            }
        )
        provenance = dict(base.compiled_source_provenance or {})
        provenance.update(
            {
                "collapse_learning_probe_source_fixture": base.fixture_name,
                "collapse_learning_probe_lambda_birth": float(lambda_birth),
            }
        )
        probes[fixture_name] = replace(
            base,
            fixture_name=fixture_name,
            notes=notes,
            compiled_source_provenance=provenance,
        )
    return probes


def _growth_collapse_relay_probe_sources() -> Mapping[str, GRCL9V3SourceDocument]:
    """Build recurrent relay probes over the delayed multi-center source."""

    base_sources = {
        source.fixture_name: source
        for source in (
            *compile_default_grcl9v3_landscape_seed_examples_to_sources(),
            *compile_legacy_grcl9v3_growth_landscape_seed_examples_to_sources(),
        )
    }
    base = base_sources[_COLLAPSE_LEARNING_PROBE_SOURCE]
    probes: dict[str, GRCL9V3SourceDocument] = {}
    for suffix, lambda_birth in _GROWTH_COLLAPSE_RELAY_PROBES:
        fixture_name = f"growth_collapse_relay_probe_{suffix}_control"
        notes = dict(base.notes or {})
        runtime_overrides = dict(notes.get("runtime_diagnostic_overrides", {}))
        runtime_overrides["lambda_birth"] = float(lambda_birth)
        notes.update(
            {
                "boundary": (
                    "runtime recurrent growth/collapse relay probe over the "
                    "delayed multi-center GRCL-9V3 source; this is not a new "
                    "source ontology term"
                ),
                "relay_probe_source_fixture": base.fixture_name,
                "relay_probe_lambda_birth": float(lambda_birth),
                "relay_probe_expected_selector_ids": (
                    "growth_events",
                    "choice_collapse_events",
                    "basin_assignment_learning",
                    "growth_collapse_relay_diagnostics",
                ),
                "runtime_diagnostic_overrides": runtime_overrides,
            }
        )
        provenance = dict(base.compiled_source_provenance or {})
        provenance.update(
            {
                "relay_probe_source_fixture": base.fixture_name,
                "relay_probe_lambda_birth": float(lambda_birth),
            }
        )
        probes[fixture_name] = replace(
            base,
            fixture_name=fixture_name,
            notes=notes,
            compiled_source_provenance=provenance,
        )
    return probes


def _relay_port_probe_sources() -> Mapping[str, GRCL9V3SourceDocument]:
    """Build relay-port geometry probes over the delayed multi-center source."""

    base_sources = {
        source.fixture_name: source
        for source in (
            *compile_default_grcl9v3_landscape_seed_examples_to_sources(),
            *compile_legacy_grcl9v3_growth_landscape_seed_examples_to_sources(),
        )
    }
    base = base_sources[_COLLAPSE_LEARNING_PROBE_SOURCE]
    probes: dict[str, GRCL9V3SourceDocument] = {}
    for suffix, runtime_overrides, relay_profile in _RELAY_PORT_PROBES:
        fixture_name = f"relay_port_probe_{suffix}_control"
        notes = dict(base.notes or {})
        overrides = dict(notes.get("runtime_diagnostic_overrides", {}))
        overrides.update({key: float(value) for key, value in runtime_overrides.items()})
        notes.update(
            {
                "boundary": (
                    "runtime relay-port geometry probe over the delayed "
                    "multi-center GRCL-9V3 source; this declares a birth-port "
                    "sink-then-source scaffold, not a solved relay outcome"
                ),
                "relay_port_probe_source_fixture": base.fixture_name,
                "relay_port_probe_runtime_overrides": dict(overrides),
                "relay_port_probe_growth_profile": dict(relay_profile),
                "relay_probe_expected_selector_ids": (
                    "growth_events",
                    "choice_collapse_events",
                    "basin_assignment_learning",
                    "growth_collapse_relay_diagnostics",
                ),
                "runtime_diagnostic_overrides": overrides,
            }
        )
        provenance = dict(base.compiled_source_provenance or {})
        provenance.update(
            {
                "relay_port_probe_source_fixture": base.fixture_name,
                "relay_port_probe_runtime_overrides": dict(overrides),
                "relay_port_probe_growth_profile": dict(relay_profile),
            }
        )
        probes[fixture_name] = replace(
            base,
            fixture_name=fixture_name,
            constructs=_relay_port_constructs(base, relay_profile),
            notes=notes,
            compiled_source_provenance=provenance,
        )
    return probes


def _relay_port_constructs(
    source: GRCL9V3SourceDocument,
    relay_profile: Mapping[str, Any],
) -> tuple[Any, ...]:
    constructs: list[Any] = []
    for construct in source.constructs:
        if isinstance(construct, GRCL9V3GrowthLocus):
            profile = dict(construct.outward_pressure_profile or {})
            profile.update(relay_profile)
            constructs.append(replace(construct, outward_pressure_profile=profile))
        else:
            constructs.append(construct)
    return tuple(constructs)


def _hessian_backend_probe_sources() -> Mapping[str, GRCL9V3SourceDocument]:
    """Build paired runtime diagnostic sources over existing seed-backed examples."""

    base_sources = {
        source.fixture_name: source
        for source in compile_default_grcl9v3_landscape_seed_examples_to_sources()
    }
    probes: dict[str, GRCL9V3SourceDocument] = {}
    for pair_id, source_fixture_name in _HESSIAN_BACKEND_PROBE_BASES:
        base = base_sources[source_fixture_name]
        for suffix, backend, selector_id in _HESSIAN_BACKEND_PROBE_BACKENDS:
            fixture_name = f"hessian_probe_{pair_id}_{suffix}_control"
            diagnostic_selector_ids = (
                (selector_id,)
                if pair_id == "quiescent_isotropic"
                else (selector_id, "hybrid_tensor_available")
            )
            notes = dict(base.notes or {})
            notes.update(
                {
                    "boundary": (
                        "runtime Hessian backend probe over an existing seed-backed "
                        "GRCL-9V3 source; this is not a new source ontology term"
                    ),
                    "hessian_probe_pair_id": pair_id,
                    "hessian_probe_source_fixture": source_fixture_name,
                    "hessian_probe_expected_selector_ids": diagnostic_selector_ids,
                    "runtime_diagnostic_overrides": {"hessian_backend": backend},
                }
            )
            provenance = dict(base.compiled_source_provenance or {})
            provenance.update(
                {
                    "hessian_probe_pair_id": pair_id,
                    "hessian_probe_source_fixture": source_fixture_name,
                    "runtime_diagnostic_backend": backend,
                }
            )
            probes[fixture_name] = replace(
                base,
                fixture_name=fixture_name,
                notes=notes,
                compiled_source_provenance=provenance,
            )
    return probes


def _write_landscape_examples(
    root: Path,
    fixture_names: Sequence[str],
    *,
    source_mode: str,
) -> None:
    examples = (
        grcl9v3_landscape_seed_example_by_name()
        if source_mode == "landscape_seed_examples"
        else grcl9v3_landscape_example_by_name()
    )
    for fixture_name in fixture_names:
        _write_json(root / f"{fixture_name}.json", examples[fixture_name].to_mapping())


def _write_landscape_seeds(root: Path, fixture_names: Sequence[str]) -> None:
    paths = grcl9v3_landscape_seed_example_path_by_name()
    for fixture_name in fixture_names:
        source = paths[fixture_name]
        _write_text(root / source.name, source.read_text(encoding="utf-8"))


def _run_replay_lane(
    *,
    source: GRCL9V3SourceDocument,
    requested_steps: int,
    session_id: str,
    lanes_root: Path,
    sources_root: Path,
    lowered_root: Path,
    reports_root: Path,
) -> GRCL9V3ReplayLaneResult:
    runtime_config = _runtime_config_for_source(source)
    params = GRC9V3.from_config(runtime_config).get_params()
    lowered = lower_grcl9v3_source_to_grc9v3_state(source, params=params)
    model = GRC9V3(params=params, state=lowered.state)
    seed_path = f"grcl9v3/lowering/source_fixtures/{source.fixture_name}.json"
    identity = _run_identity(
        params=params,
        source=source,
        seed_path=seed_path,
        requested_steps=requested_steps,
    )
    lane_context = GRC9V3LaneContext(
        source_reference=GRCL9V3_SOURCE_REFERENCE,
        fixture_name=source.fixture_name,
        run_role=_control_role_for_source(source),
        experiment_id=f"grcl9v3_lowering_{session_id.lower()}",
        representative_lane_name=source.fixture_name,
        source_runtime_artifact=seed_path,
    )
    shared_extensions = _shared_extensions(source, lowered.state)
    checkpoint_config = GraphCheckpointCaptureConfig(
        include_initial=True,
        include_final=True,
        every_step=True,
        include_flow_overlays=True,
        storage_mode="per_checkpoint_files",
    )
    snapshots_dir = lanes_root / source.fixture_name / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    initial_snapshot_path = snapshots_dir / "initial_snapshot.json"
    final_snapshot_path = snapshots_dir / "final_snapshot.json"
    model.save(str(initial_snapshot_path))
    initial_observables = dict(model.compute_observables())

    primary = _execute_run(
        model,
        identity=identity,
        lane_context=lane_context,
        requested_steps=requested_steps,
        build_checkpoints=True,
    )
    model.save(str(final_snapshot_path))
    final_digest = digest_snapshot(model.snapshot())

    replay_model = GRC9V3.load(str(initial_snapshot_path))
    replay = _execute_run(
        replay_model,
        identity=identity,
        lane_context=lane_context,
        requested_steps=requested_steps,
        build_checkpoints=False,
    )
    replay_digest = digest_snapshot(replay_model.snapshot())

    replay_probe = capture_run_telemetry(
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=source.fixture_name,
        seed_source_reference=GRCL9V3_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family="grcl9v3_lowering_replay",
        rng_seed=int(params.evolution.get("rng_seed", 0)),
        requested_steps=requested_steps,
        initial_observables=initial_observables,
        step_results=replay["step_results"],
        final_observables=dict(replay_model.compute_observables()),
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        family_extensions=shared_extensions,
        step_family_extensions=replay["step_family_extensions"],
        event_family_extensions_by_step=replay["event_family_extensions_by_step"],
    )
    replay_step_rows_match = replay_probe.step_rows == tuple(
        _step_rows_for_compare(
            step_results=primary["step_results"],
            identity=identity,
            family_extensions=shared_extensions,
            step_family_extensions=primary["step_family_extensions"],
        )
    )
    replay_event_rows_match = replay_probe.event_rows == tuple(
        _event_rows_for_compare(
            step_results=primary["step_results"],
            identity=identity,
            family_extensions=shared_extensions,
            event_family_extensions_by_step=primary["event_family_extensions_by_step"],
        )
    )
    replay_digest_match = replay_digest == final_digest

    summary_extension = grc9v3_run_summary_family_extensions(
        _build_grc9v3_run_summary_extension(
            model,
            primary["step_results"],
            lane_context=lane_context,
            replay_digest_match=(
                replay_step_rows_match and replay_event_rows_match and replay_digest_match
            ),
        )
    )
    telemetry = capture_run_telemetry(
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=source.fixture_name,
        seed_source_reference=GRCL9V3_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family="grcl9v3_lowering_replay",
        rng_seed=int(params.evolution.get("rng_seed", 0)),
        requested_steps=requested_steps,
        initial_observables=initial_observables,
        step_results=primary["step_results"],
        final_observables=dict(model.compute_observables()),
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        family_extensions=shared_extensions,
        step_family_extensions=primary["step_family_extensions"],
        event_family_extensions_by_step=primary["event_family_extensions_by_step"],
        summary_family_extensions=summary_extension,
        graph_checkpoints=primary["graph_checkpoints"],
        graph_checkpoint_index=_checkpoint_index(
            identity,
            primary["graph_checkpoints"],
            requested_steps=requested_steps,
        ),
        artifact_layout=build_telemetry_artifact_layout(source.fixture_name, root_dir=lanes_root),
        config=TelemetryCaptureConfig(
            root_dir=lanes_root,
            write_artifacts=True,
            graph_checkpoints=checkpoint_config,
        ),
    )
    source_path = sources_root / f"{source.fixture_name}.json"
    lowered_path = lowered_root / f"{source.fixture_name}.json"
    replay_report_path = reports_root / f"{source.fixture_name}_replay_report.json"
    _write_json(source_path, source.to_mapping())
    _write_json(lowered_path, _lowering_result_to_mapping(lowered, params=params))
    event_counts_total = Counter(
        event.kind for step_result in primary["step_results"] for event in step_result.events
    )
    replay_report = {
        "replay_version": GRCL9V3_REPLAY_VERSION,
        "fixture_name": source.fixture_name,
        "manifest_entry_id": source.manifest_entry_id,
        "run_id": telemetry.identity.run_id,
        "requested_steps": requested_steps,
        "final_snapshot_path": str(final_snapshot_path),
        "initial_snapshot_path": str(initial_snapshot_path),
        "final_snapshot_digest": final_digest,
        "replay_final_snapshot_digest": replay_digest,
        "replay_step_rows_match": replay_step_rows_match,
        "replay_event_rows_match": replay_event_rows_match,
        "replay_digest_match": replay_digest_match,
        "event_count": len(telemetry.event_rows),
        "event_counts_by_kind": dict(sorted(event_counts_total.items())),
    }
    _write_json(replay_report_path, replay_report)
    if telemetry.artifact_layout is None:
        raise AssertionError("telemetry artifact layout was not written")
    return GRCL9V3ReplayLaneResult(
        fixture_name=source.fixture_name,
        manifest_entry_id=source.manifest_entry_id,
        run_id=telemetry.identity.run_id,
        requested_steps=requested_steps,
        artifact_root=str(telemetry.artifact_layout.run_dir),
        source_fixture_path=str(source_path),
        lowered_state_path=str(lowered_path),
        replay_report_path=str(replay_report_path),
        checkpoint_count=len(primary["graph_checkpoints"]),
        event_count=len(telemetry.event_rows),
        event_counts_by_kind=dict(sorted(event_counts_total.items())),
        replay_step_rows_match=replay_step_rows_match,
        replay_event_rows_match=replay_event_rows_match,
        replay_digest_match=replay_digest_match,
    )


def _execute_run(
    model: GRC9V3,
    *,
    identity: RunTelemetryIdentity,
    lane_context: GRC9V3LaneContext,
    requested_steps: int,
    build_checkpoints: bool,
) -> Mapping[str, Any]:
    step_results: list[Any] = []
    step_family_extensions: list[Mapping[str, Mapping[str, Any]]] = []
    event_family_extensions_by_step: list[list[Mapping[str, Mapping[str, Any]]]] = []
    graph_checkpoints: list[GraphCheckpointArtifact] = []
    if build_checkpoints:
        graph_checkpoints.append(
            _export_checkpoint(
                model=model,
                identity=identity,
                checkpoint_id="step-00000000",
                checkpoint_label="initial",
                checkpoint_reason="initial",
                event_count_window=0,
                event_counts_by_kind_window={},
            )
        )
    for _ in range(requested_steps):
        step_result = model.step()
        step_results.append(step_result)
        step_family_extensions.append(
            grc9v3_step_family_extensions(
                _build_grc9v3_step_extension(model, lane_context=lane_context)
            )
        )
        event_family_extensions_by_step.append(
            [
                grc9v3_event_family_extensions(
                    _build_grc9v3_event_extension(
                        model,
                        event,
                        lane_context=lane_context,
                    )
                )
                for event in step_result.events
            ]
        )
        if build_checkpoints:
            event_counts = Counter(event.kind for event in step_result.events)
            graph_checkpoints.append(
                _export_checkpoint(
                    model=model,
                    identity=identity,
                    checkpoint_id=f"step-{step_result.step_index:08d}",
                    checkpoint_label=(
                        "final" if step_result.step_index == requested_steps else "interval"
                    ),
                    checkpoint_reason=(
                        "final" if step_result.step_index == requested_steps else "every_step"
                    ),
                    event_count_window=len(step_result.events),
                    event_counts_by_kind_window=dict(sorted(event_counts.items())),
                )
            )
    return {
        "step_results": tuple(step_results),
        "step_family_extensions": tuple(step_family_extensions),
        "event_family_extensions_by_step": tuple(tuple(item) for item in event_family_extensions_by_step),
        "graph_checkpoints": tuple(graph_checkpoints),
    }


def _step_rows_for_compare(
    *,
    step_results: Sequence[Any],
    identity: RunTelemetryIdentity,
    family_extensions: Mapping[str, Mapping[str, Any]],
    step_family_extensions: Sequence[Mapping[str, Mapping[str, Any]]],
) -> tuple[Any, ...]:
    return capture_run_telemetry(
        model_family="grc9v3",
        params_identity=identity.params_identity,
        seed_name=identity.seed_name,
        seed_source_reference=identity.seed_source_reference,
        seed_path=identity.seed_path,
        param_family=identity.param_family,
        rng_seed=identity.rng_seed,
        requested_steps=identity.requested_steps,
        initial_observables={},
        step_results=step_results,
        final_observables={},
        family_extensions=family_extensions,
        step_family_extensions=step_family_extensions,
    ).step_rows


def _event_rows_for_compare(
    *,
    step_results: Sequence[Any],
    identity: RunTelemetryIdentity,
    family_extensions: Mapping[str, Mapping[str, Any]],
    event_family_extensions_by_step: Sequence[Sequence[Mapping[str, Mapping[str, Any]]]],
) -> tuple[Any, ...]:
    return capture_run_telemetry(
        model_family="grc9v3",
        params_identity=identity.params_identity,
        seed_name=identity.seed_name,
        seed_source_reference=identity.seed_source_reference,
        seed_path=identity.seed_path,
        param_family=identity.param_family,
        rng_seed=identity.rng_seed,
        requested_steps=identity.requested_steps,
        initial_observables={},
        step_results=step_results,
        final_observables={},
        family_extensions=family_extensions,
        event_family_extensions_by_step=event_family_extensions_by_step,
    ).event_rows


def _runtime_config_for_source(source: GRCL9V3SourceDocument) -> Mapping[str, Any]:
    evolution: dict[str, Any] = {
        "alpha": 1e-12,
        "beta": 1e-12,
        "gamma": 1e-12,
        "delta": 1e-12,
        "kappa_c": 1.0,
        "eta": 1.0,
        "rng_seed": 0,
        "eps_spark": 0.05,
        "tau_instability": 999.0,
        "lambda_birth": 0.0,
        "alpha_seed": 0.25,
        "w_bond": 1.0,
        "site_potential_selection": "quadratic",
        "site_potential_params": {"scale": 1.0, "mu": 0.0},
    }
    modes: dict[str, Any] = {
        "frame_mode": "fixed_port_chart",
        "curvature_backend": "none",
        "boundary_mode": "prune",
        "expansion_distribution_mode": "equal",
        "edge_label_selection": "all",
        "hessian_backend": "row_basis_diagonal",
    }
    for construct in source.constructs:
        if isinstance(construct, GRCL9V3HybridSparkRegion):
            evolution["eps_spark"] = float(construct.spark_threshold)
        elif isinstance(construct, GRCL9V3ExpansionRefinementRegion):
            evolution["D_eff_target"] = int(construct.target_effective_degree)
            evolution["expansion_custom_weights"] = tuple(
                construct.coherence_transfer_ratios
            )
            modes["expansion_distribution_mode"] = construct.expansion_distribution_mode
        elif isinstance(construct, GRCL9V3GrowthLocus):
            evolution["lambda_birth"] = float(construct.lambda_birth)
            modes["growth_parent_eligibility"] = (
                "grcl9v3_front_capacity"
                if construct.growth_semantics == "front_capacity"
                else "legacy_any_inactive_port"
            )
        elif isinstance(construct, GRCL9V3ChoiceCollapseRegion):
            modes["choice_backend"] = "sink_compatibility"
            evolution["kappa_c"] = 1e-12
        elif isinstance(construct, GRCL9V3AppendixEDivisionRegion):
            evolution["identity_fission_min_basin_mass"] = 0.0
            evolution["identity_fission_persistence_delta"] = 3
    if {
        "no_lifecycle_events",
        "no_choice_collapse_events",
    } & set(source.expected_selector_ids):
        modes["choice_backend"] = "disabled"
    runtime_overrides = dict(
        source.notes.get("runtime_diagnostic_overrides", {})
        if isinstance(source.notes, Mapping)
        and isinstance(source.notes.get("runtime_diagnostic_overrides"), Mapping)
        else {}
    )
    hessian_backend = runtime_overrides.get("hessian_backend")
    if hessian_backend is not None:
        if hessian_backend not in {"row_basis_diagonal", "weighted_least_squares"}:
            raise ValueError("unsupported Hessian backend diagnostic override")
        modes["hessian_backend"] = str(hessian_backend)
    lambda_birth_override = runtime_overrides.get("lambda_birth")
    if lambda_birth_override is not None:
        lambda_birth = float(lambda_birth_override)
        if lambda_birth < 0.0:
            raise ValueError("lambda_birth diagnostic override must be nonnegative")
        evolution["lambda_birth"] = lambda_birth
    for key in ("alpha_seed", "w_bond", "eta", "kappa_c"):
        value = runtime_overrides.get(key)
        if value is None:
            continue
        numeric_value = float(value)
        if key in {"alpha_seed", "w_bond", "eta"} and numeric_value < 0.0:
            raise ValueError(f"{key} diagnostic override must be nonnegative")
        if key == "alpha_seed" and numeric_value > 1.0:
            raise ValueError("alpha_seed diagnostic override must be <= 1")
        evolution[key] = numeric_value
    return {
        "dt": 0.1,
        "evolution": evolution,
        "constitutive_semantic_modes": modes,
    }


def _shared_extensions(
    source: GRCL9V3SourceDocument,
    state: GRC9V3State,
) -> Mapping[str, Mapping[str, Any]]:
    expected_caches = _expected_region_caches(state)
    return {
        "grcl9v3": {
            "replay_version": GRCL9V3_REPLAY_VERSION,
            "source_schema_version": source.source_schema_version,
            "lowering_manifest_version": GRCL9V3_LOWERING_MANIFEST_VERSION,
            "projector_revision": GRCL9V3_PROJECTOR_REVISION,
            "lowering_mode": GRCL9V3_LOWERING_MODE,
            "fixture_name": source.fixture_name,
            "manifest_entry_id": source.manifest_entry_id,
            "expected_selector_ids": list(source.expected_selector_ids),
            "source_construct_kinds": [
                construct.construct_kind for construct in source.constructs
            ],
            "expected_region_caches": expected_caches,
            "expected_region_cache_names": sorted(expected_caches),
            "growth_semantics_status": state.cached_quantities.get(
                "grcl9v3_growth_semantics_status",
                "none",
            ),
            "growth_parent_eligibility_mode": state.cached_quantities.get(
                "birth_parent_eligibility_mode",
                "grcl9v3_front_capacity"
                if state.cached_quantities.get("grcl9v3_growth_semantics_status")
                == "front_capacity"
                else "legacy_any_inactive_port",
            ),
            "growth_parent_capacity_sources": canonicalize_json_value(
                state.cached_quantities.get(
                    "grcl9v3_growth_parent_capacity_sources",
                    {},
                )
            ),
            "front_growth_eligible_ports": canonicalize_json_value(
                state.cached_quantities.get("grcl9v3_front_growth_eligible_ports", {})
            ),
            "legacy_growth_locus_ids": list(
                state.cached_quantities.get("grcl9v3_legacy_growth_locus_ids", ())
            ),
        }
    }


def _expected_region_caches(state: GRC9V3State) -> dict[str, Any]:
    return {
        key: canonicalize_json_value(value)
        for key, value in sorted(state.cached_quantities.items())
        if key.startswith("grcl9v3_expected_")
    }


def _export_checkpoint(
    *,
    model: GRC9V3,
    identity: RunTelemetryIdentity,
    checkpoint_id: str,
    checkpoint_label: str,
    checkpoint_reason: str,
    event_count_window: int,
    event_counts_by_kind_window: Mapping[str, int],
) -> GraphCheckpointArtifact:
    state = model.get_state()
    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=state.step_index,
        time=state.time,
        checkpoint_label=checkpoint_label,
        checkpoint_reason=checkpoint_reason,
        graph_kind="port_graph",
        node_count=len(tuple(state.topology.iter_live_node_ids())),
        edge_count=len(tuple(state.topology.iter_live_edge_ids())),
        node_records=_node_records(model),
        edge_records=_edge_records(model),
        event_step_range={
            "start_step_inclusive": state.step_index,
            "end_step_inclusive": state.step_index,
        },
        event_count_window=event_count_window,
        event_counts_by_kind_window=dict(event_counts_by_kind_window),
        flow_representation="signed_port_flux",
        flow_cadence="checkpoint_only",
        label_computation_modes=dict(state.edge_label_computation_mode),
        topology_extensions={
            "next_node_id": state.topology.next_node_id,
            "next_edge_id": state.topology.next_edge_id,
        },
        family_extensions=_checkpoint_family_extensions(model),
    )


def _checkpoint_family_extensions(model: GRC9V3) -> Mapping[str, Mapping[str, Any]]:
    state = model.get_state()
    expected_caches = _expected_region_caches(state)
    return {
        "grc9v3": {
            "contract_version": GRC9V3_TELEMETRY_CONTRACT_VERSION,
            "checkpoint_surface": "phase_t_grc9v3_lowered_source_overlays",
            "node_overlay": _checkpoint_node_overlay(model),
            "port_overlay": _checkpoint_port_overlay(model),
            "edge_overlay": _checkpoint_edge_overlay(model),
            "module_overlay": _checkpoint_module_overlay(model),
            "choice_overlay": _checkpoint_choice_overlay(model),
        },
        "grcl9v3": {
            "replay_version": GRCL9V3_REPLAY_VERSION,
            "source_fixture_name": state.cached_quantities.get("grcl9v3_source_fixture_name"),
            "manifest_entry_id": state.cached_quantities.get("grcl9v3_manifest_entry_id"),
            "provenance_available": "grcl9v3_provenance" in state.cached_quantities,
            "motif_registry_available": "grcl9v3_motif_registry" in state.cached_quantities,
            "bridge_edge_ids": list(state.cached_quantities.get("grcl9v3_bridge_edge_ids", ())),
            "expected_region_caches": expected_caches,
            "expected_region_cache_names": sorted(expected_caches),
            "growth_semantics_status": state.cached_quantities.get(
                "grcl9v3_growth_semantics_status",
                "none",
            ),
            "growth_parent_capacity_sources": canonicalize_json_value(
                state.cached_quantities.get(
                    "grcl9v3_growth_parent_capacity_sources",
                    {},
                )
            ),
            "front_growth_eligible_ports": canonicalize_json_value(
                state.cached_quantities.get("grcl9v3_front_growth_eligible_ports", {})
            ),
            "legacy_growth_locus_ids": list(
                state.cached_quantities.get("grcl9v3_legacy_growth_locus_ids", ())
            ),
        },
    }


def _checkpoint_node_overlay(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    module_node_ids = _module_node_ids(state)
    latest_candidate_by_node = _latest_column_h_candidate_by_node(state)
    raw_current_column_h = state.cached_quantities.get("current_column_h_by_node")
    current_column_h_by_node = (
        raw_current_column_h if isinstance(raw_current_column_h, Mapping) else {}
    )
    overlay: dict[str, Any] = {}
    for node_id, node in (
        (node_id, state.nodes.get(node_id))
        for node_id in sorted(state.topology.iter_live_node_ids())
    ):
        node_payload: dict[str, Any] = {
            "coherence": None if node is None else float(node.coherence),
            "gradient_norm": None
            if node is None
            else float(sum(value * value for value in node.gradient_row_basis) ** 0.5),
            "min_signed_hessian": None
            if node is None or not node.signed_hessian_row_basis
            else float(min(node.signed_hessian_row_basis)),
            "basin_mass": None if node is None else float(node.basin_mass),
            "basin_id": None if node is None else str(node.basin_id),
            "parent_id": None if node is None or node.parent_id is None else str(node.parent_id),
            "depth": None if node is None else int(node.depth),
            "is_sink": node_id in state.sink_set,
            "is_module_node": node_id in module_node_ids,
        }
        latest_candidate = latest_candidate_by_node.get(node_id)
        cached_column_h = current_column_h_by_node.get(str(node_id))
        if latest_candidate is not None:
            node_payload.update(
                {
                    "spark_lane": latest_candidate.get("spark_lane"),
                    "column_h_computation_version": latest_candidate.get(
                        "column_h_computation_version"
                    ),
                    "column_h": list(latest_candidate.get("column_h", ())),
                    "min_abs_column_h": latest_candidate.get("min_abs_column_h"),
                    "min_abs_column_h_column": latest_candidate.get(
                        "min_abs_column_h_column"
                    ),
                    "column_h_branch_hit": latest_candidate.get("column_h_branch_hit"),
                    "column_h_gate_reasons": list(
                        latest_candidate.get("gate_reasons", ())
                    ),
                    "column_h_diagnostic_source": "latest_candidate_event",
                }
            )
        elif cached_column_h is not None:
            abs_column_h = [abs(float(value)) for value in cached_column_h]
            min_abs_column_h = min(abs_column_h) if abs_column_h else None
            node_payload.update(
                {
                    "spark_lane": state.cached_quantities.get(
                        "current_column_h_spark_lane"
                    ),
                    "column_h_computation_version": state.cached_quantities.get(
                        "column_h_computation_version"
                    ),
                    "column_h": list(cached_column_h),
                    "min_abs_column_h": min_abs_column_h,
                    "min_abs_column_h_column": (
                        int(abs_column_h.index(min_abs_column_h) + 1)
                        if min_abs_column_h is not None
                        else None
                    ),
                    "column_h_diagnostic_source": "current_column_h_cache",
                }
            )
        overlay[str(node_id)] = node_payload
    return overlay


def _latest_column_h_candidate_by_node(state: Any) -> dict[int, Mapping[str, Any]]:
    latest_by_node: dict[int, Mapping[str, Any]] = {}
    for event in state.event_log:
        if event.kind != "hybrid_spark_candidate":
            continue
        payload = event.payload
        if "column_h" not in payload:
            continue
        node_id = payload.get("node_id", payload.get("candidate_node_id"))
        if node_id is None:
            continue
        latest_by_node[int(node_id)] = payload
    return latest_by_node


def _checkpoint_port_overlay(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    row_totals = [0, 0, 0]
    column_totals = [0, 0, 0]
    by_node: dict[str, Any] = {}
    for node_id in sorted(state.topology.iter_live_node_ids()):
        occupied_ports: list[int] = []
        free_ports: list[int] = []
        for port_id in range(1, 10):
            if state.topology.port_is_occupied(node_id, port_id - 1):
                occupied_ports.append(port_id)
                row, column = port_to_rc(port_id)
                row_totals[row - 1] += 1
                column_totals[column - 1] += 1
            else:
                free_ports.append(port_id)
        by_node[str(node_id)] = {
            "occupied_ports": occupied_ports,
            "free_ports": free_ports,
            "active_degree": len(occupied_ports),
            "saturated": len(occupied_ports) == 9,
        }
    return {
        "by_node": by_node,
        "row_totals": tuple(row_totals),
        "column_totals": tuple(column_totals),
        "saturated_node_ids": tuple(
            int(node_id)
            for node_id, payload in by_node.items()
            if bool(payload["saturated"])
        ),
    }


def _checkpoint_edge_overlay(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    return {
        str(edge_id): {
            "base_conductance": float(
                state.base_conductance.get(edge_id, state.port_edges[edge_id].conductance)
            ),
            "flux_uv": float(state.port_edges[edge_id].flux_uv),
            "geometric_length": (
                None if edge_id not in state.geometric_length else float(state.geometric_length[edge_id])
            ),
            "temporal_delay": (
                None if edge_id not in state.temporal_delay else float(state.temporal_delay[edge_id])
            ),
            "flux_coupling": (
                None if edge_id not in state.flux_coupling else float(state.flux_coupling[edge_id])
            ),
        }
        for edge_id in sorted(state.topology.iter_live_edge_ids())
    }


def _checkpoint_module_overlay(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    return {
        "expansions": {
            str(expansion_id): {
                "parent_sink_id": int(record.parent_sink_id),
                "module_node_ids": tuple(int(node_id) for node_id in record.module_node_ids),
                "expansion_step": int(record.expansion_step),
                "distribution_weights": tuple(float(value) for value in record.distribution_weights),
            }
            for expansion_id, record in sorted(state.expansion_registry.items())
        }
    }


def _checkpoint_choice_overlay(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    return {
        "choice_registry": _plain_json_mapping(state.choice_registry),
        "collapse_registry": _plain_json_mapping(state.collapse_registry),
    }


def _node_records(model: GRC9V3) -> tuple[dict[str, Any], ...]:
    state = model.get_state()
    records: list[dict[str, Any]] = []
    for node_id in sorted(state.topology.iter_live_node_ids()):
        node = state.nodes.get(node_id)
        payload = state.topology.node_payload(node_id)
        records.append(
            {
                "node_id": node_id,
                "role": payload.get("grcl9v3_motif_role") or payload.get("role"),
                "coherence": None if node is None else float(node.coherence),
                "basin_mass": None if node is None else float(node.basin_mass),
                "basin_id": None if node is None else str(node.basin_id),
                "parent_id": None if node is None or node.parent_id is None else str(node.parent_id),
                "depth": None if node is None else int(node.depth),
                "is_sink": node_id in state.sink_set,
                "active_degree": len(tuple(state.topology.incident_edge_ids(node_id))),
                "payload": dict(payload),
            }
        )
    return tuple(records)


def _edge_records(model: GRC9V3) -> tuple[dict[str, Any], ...]:
    state = model.get_state()
    records: list[dict[str, Any]] = []
    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        port_edge = state.port_edges[edge_id]
        payload = state.topology.edge_payload(edge_id)
        records.append(
            {
                "edge_id": edge_id,
                "source_node_id": endpoint_a[0],
                "source_port_id": endpoint_a[1] + 1,
                "target_node_id": endpoint_b[0],
                "target_port_id": endpoint_b[1] + 1,
                "conductance": float(port_edge.conductance),
                "base_conductance": float(state.base_conductance.get(edge_id, port_edge.conductance)),
                "signed_flux_source_to_target": float(port_edge.flux_uv),
                "role": payload.get("grcl9v3_motif_role") or payload.get("role") or payload.get("kind"),
                "payload": dict(payload),
            }
        )
    return tuple(records)


def _checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: Sequence[GraphCheckpointArtifact],
    *,
    requested_steps: int,
) -> GraphCheckpointIndex:
    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="initial+every_step",
        selection_params={
            "include_initial": True,
            "every_step": True,
            "requested_steps": requested_steps,
            "surface": "phase_t_grc9v3_lowered_source_overlays",
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
                "checkpoint_surface": "phase_t_grc9v3_lowered_source_overlays",
            },
            "grcl9v3": {
                "replay_version": GRCL9V3_REPLAY_VERSION,
            },
        },
    )


def _lowering_result_to_mapping(
    result: GRCL9V3LoweringResult,
    *,
    params: GRCParams,
) -> Mapping[str, Any]:
    state = result.state
    return {
        "fixture_name": result.source.fixture_name,
        "manifest_entry_id": result.source.manifest_entry_id,
        "params_identity": params.params_hash,
        "topology": export_port_topology(state.topology),
        "nodes": {
            str(node_id): _node_state_to_mapping(node)
            for node_id, node in sorted(state.nodes.items())
        },
        "port_edges": {
            str(edge_id): _port_edge_to_mapping(edge)
            for edge_id, edge in sorted(state.port_edges.items())
        },
        "base_conductance": {
            str(edge_id): value for edge_id, value in sorted(state.base_conductance.items())
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
        "hierarchy": dict(state.hierarchy),
        "budget_target": state.budget_target,
        "cached_quantities": canonicalize_json_value(dict(state.cached_quantities)),
        "node_id_by_role": dict(sorted(result.node_id_by_role.items())),
        "edge_id_by_role": dict(sorted(result.edge_id_by_role.items())),
    }


def _node_state_to_mapping(node: GRC9V3NodeState) -> Mapping[str, Any]:
    return {
        "coherence": node.coherence,
        "gradient_row_basis": list(node.gradient_row_basis),
        "signed_hessian_row_basis": list(node.signed_hessian_row_basis),
        "net_flux_summary": list(node.net_flux_summary),
        "basin_mass": node.basin_mass,
        "basin_id": node.basin_id,
        "parent_id": node.parent_id,
        "depth": node.depth,
    }


def _port_edge_to_mapping(edge: PortEdge) -> Mapping[str, Any]:
    return {
        "node_u": edge.node_u,
        "port_u": edge.port_u,
        "node_v": edge.node_v,
        "port_v": edge.port_v,
        "conductance": edge.conductance,
        "flux_uv": edge.flux_uv,
    }


def _run_identity(
    *,
    params: GRCParams,
    source: GRCL9V3SourceDocument,
    seed_path: str,
    requested_steps: int,
) -> RunTelemetryIdentity:
    run_id = build_run_id(
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=source.fixture_name,
        seed_source_reference=GRCL9V3_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family="grcl9v3_lowering_replay",
        rng_seed=int(params.evolution.get("rng_seed", 0)),
        requested_steps=requested_steps,
        overrides=None,
    )
    return RunTelemetryIdentity(
        run_id=run_id,
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=source.fixture_name,
        seed_source_reference=GRCL9V3_SOURCE_REFERENCE,
        seed_path=seed_path,
        param_family="grcl9v3_lowering_replay",
        rng_seed=int(params.evolution.get("rng_seed", 0)),
        requested_steps=requested_steps,
    )


def _session_manifest(
    *,
    session_id: str,
    session_root: Path,
    lanes: Sequence[GRCL9V3ReplayLaneResult],
    replay_script_path: Path,
    requested_steps: int,
    fixture_names: Sequence[str],
    source_mode: str,
    extra_report_paths: Mapping[str, str] | None = None,
) -> Mapping[str, Any]:
    replay_command = _replay_command(
        session_id=session_id,
        requested_steps=requested_steps,
        fixture_names=fixture_names,
        source_mode=source_mode,
    )
    input_documents = [
        "implementation/GRCL-9V3-ImplementationPlan.md",
        "implementation/GRCL-9V3-ImplementationChecklist.md",
        "implementation/GRCL-9V3-Vocabulary.md",
        GRC9V3_TELEMETRY_SOURCE_REFERENCE,
    ]
    if source_mode in {
        "collapse_learning_probe",
        "growth_collapse_relay_probe",
        "landscape_examples",
        "landscape_seed_examples",
        "legacy_growth_landscape_seed_examples",
        "hessian_backend_probe",
    }:
        input_documents.append("src/pygrc/landscapes/extensions/grcl9v3/examples.py")
    if source_mode == "landscape_seed_examples":
        input_documents.extend(
            str(path) for path in grcl9v3_landscape_seed_example_path_by_name().values()
        )
    if source_mode == "legacy_growth_landscape_seed_examples":
        input_documents.extend(
            str(path)
            for path in legacy_grcl9v3_growth_landscape_seed_example_path_by_name().values()
        )
    return {
        "session_id": session_id,
        "session_kind": "grcl9v3_lowering_replay",
        "source_mode": source_mode,
        "replay_version": GRCL9V3_REPLAY_VERSION,
        "session_root": str(session_root),
        "source_schema_version": "grcl9v3.source.v1",
        "lowering_manifest_version": GRCL9V3_LOWERING_MANIFEST_VERSION,
        "projector_revision": GRCL9V3_PROJECTOR_REVISION,
        "lowering_mode": GRCL9V3_LOWERING_MODE,
        "input_documents": input_documents,
        "lane_count": len(lanes),
        "lanes": [lane.to_mapping() for lane in lanes],
        "replay_script_path": str(replay_script_path),
        "replay_command": replay_command,
        "extra_report_paths": dict(extra_report_paths or {}),
    }


def _write_replay_script(
    path: Path,
    *,
    session_id: str,
    requested_steps: int,
    fixture_names: Sequence[str],
    source_mode: str,
) -> None:
    text = (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"{_replay_command(session_id=session_id, requested_steps=requested_steps, fixture_names=fixture_names, source_mode=source_mode)}\n"
    )
    _write_text(path, text)
    current_mode = path.stat().st_mode
    path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _replay_command(
    *,
    session_id: str,
    requested_steps: int,
    fixture_names: Sequence[str],
    source_mode: str,
) -> str:
    args = " ".join(f"--fixture {name}" for name in fixture_names)
    return (
        "PYTHONPATH=src python -m pygrc.telemetry.grcl9v3_replay "
        f"--session-id {session_id} --steps {requested_steps} "
        f"--source-mode {source_mode} {args}"
    ).rstrip()


def _write_experimental_log(
    path: Path,
    *,
    session_id: str,
    session_root: Path,
    lanes: Sequence[GRCL9V3ReplayLaneResult],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    total_events = sum(lane.event_count for lane in lanes)
    row = (
        f"| {session_id} | Lowered-source replay smoke session | "
        f"{len(lanes)} | {total_events} | `{session_root}` |"
    )
    existing_rows: list[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("| S") and line[3:4].isdigit():
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if cells and cells[0] != session_id:
                    existing_rows.append(line)
    lines = [
        "# GRCL-9V3 Lowering Experimental Log",
        "",
        "Sessions are replayable records under `outputs/grcl9v3/lowering/sessions/`.",
        "",
        "| Session | Purpose | Lanes | Events | Root |",
        "|---|---|---:|---:|---|",
        *existing_rows,
        row,
        "",
    ]
    _write_text(path, "\n".join(lines))


def _hessian_backend_probe_report(
    lanes: Sequence[GRCL9V3ReplayLaneResult],
) -> Mapping[str, Any]:
    by_pair: dict[str, dict[str, GRCL9V3ReplayLaneResult]] = {}
    for lane in lanes:
        pair_id, backend = _hessian_pair_id_and_backend(lane.fixture_name)
        by_pair.setdefault(pair_id, {})[backend] = lane

    pairs: list[Mapping[str, Any]] = []
    for pair_id in sorted(by_pair):
        lane_by_backend = by_pair[pair_id]
        row_lane = lane_by_backend.get("row_basis_diagonal")
        wls_lane = lane_by_backend.get("weighted_least_squares")
        if row_lane is None or wls_lane is None:
            pairs.append(
                {
                    "pair_id": pair_id,
                    "pair_status": "incomplete",
                    "available_backends": sorted(lane_by_backend),
                }
            )
            continue
        row_summary = _hessian_lane_summary(row_lane)
        wls_summary = _hessian_lane_summary(wls_lane)
        deltas = _hessian_pair_deltas(row_summary, wls_summary)
        largest_field = max(deltas, key=lambda key: abs(float(deltas[key]))) if deltas else None
        event_delta = (
            row_summary["event_counts_by_kind"] != wls_summary["event_counts_by_kind"]
        )
        pairs.append(
            {
                "pair_id": pair_id,
                "pair_status": "complete",
                "row_basis_lane": row_lane.fixture_name,
                "weighted_least_squares_lane": wls_lane.fixture_name,
                "event_delta_found": event_delta,
                "event_counts_by_backend": {
                    "row_basis_diagonal": row_summary["event_counts_by_kind"],
                    "weighted_least_squares": wls_summary["event_counts_by_kind"],
                },
                "metric_deltas": deltas,
                "largest_delta_field": largest_field,
                "largest_delta_value": None if largest_field is None else deltas[largest_field],
                "row_basis_summary": row_summary,
                "weighted_least_squares_summary": wls_summary,
            }
        )
    ranked = sorted(
        (
            pair
            for pair in pairs
            if pair.get("pair_status") == "complete"
            and pair.get("largest_delta_value") is not None
        ),
        key=lambda pair: abs(float(pair["largest_delta_value"])),
        reverse=True,
    )
    return {
        "report_version": "grcl9v3_hessian_backend_probe_report_v1",
        "probe_scope": (
            "runtime diagnostic backend comparison over existing seed-backed "
            "GRCL-9V3 sources; not a new source ontology claim"
        ),
        "pair_count": len(pairs),
        "complete_pair_count": sum(1 for pair in pairs if pair.get("pair_status") == "complete"),
        "event_delta_pair_count": sum(1 for pair in pairs if pair.get("event_delta_found")),
        "largest_divergence_pair_id": None if not ranked else ranked[0]["pair_id"],
        "ranked_pair_ids_by_largest_delta": [str(pair["pair_id"]) for pair in ranked],
        "delta_fields": list(_HESSIAN_DELTA_FIELDS),
        "pairs": pairs,
    }


def _hessian_pair_id_and_backend(fixture_name: str) -> tuple[str, str]:
    prefix = "hessian_probe_"
    if not fixture_name.startswith(prefix):
        raise ValueError(f"{fixture_name!r} is not a Hessian probe lane")
    stem = fixture_name[len(prefix) :]
    if stem.endswith("_weighted_least_squares_control"):
        return stem[: -len("_weighted_least_squares_control")], "weighted_least_squares"
    if stem.endswith("_row_basis_control"):
        return stem[: -len("_row_basis_control")], "row_basis_diagonal"
    raise ValueError(f"{fixture_name!r} does not encode a Hessian backend")


def _hessian_lane_summary(lane: GRCL9V3ReplayLaneResult) -> Mapping[str, Any]:
    telemetry_root = Path(lane.artifact_root) / "telemetry"
    steps = _read_jsonl(telemetry_root / "steps.jsonl")
    backend_values = _series(steps, "family_extensions.grc9v3.backend_config.hessian_backend")
    summary: dict[str, Any] = {
        "fixture_name": lane.fixture_name,
        "event_counts_by_kind": dict(lane.event_counts_by_kind),
        "event_count": lane.event_count,
        "backend_values": backend_values,
    }
    for field_path in _HESSIAN_DELTA_FIELDS:
        values = [
            value
            for value in _series(steps, field_path)
            if isinstance(value, int | float) and not isinstance(value, bool)
        ]
        summary[field_path] = {
            "first": None if not values else float(values[0]),
            "last": None if not values else float(values[-1]),
            "max_abs": None if not values else max(abs(float(value)) for value in values),
        }
    return summary


def _hessian_pair_deltas(
    row_summary: Mapping[str, Any],
    wls_summary: Mapping[str, Any],
) -> Mapping[str, float]:
    deltas: dict[str, float] = {}
    for field_path in _HESSIAN_DELTA_FIELDS:
        row_field = row_summary.get(field_path, {})
        wls_field = wls_summary.get(field_path, {})
        if not isinstance(row_field, Mapping) or not isinstance(wls_field, Mapping):
            continue
        row_value = row_field.get("max_abs")
        wls_value = wls_field.get("max_abs")
        if isinstance(row_value, int | float) and isinstance(wls_value, int | float):
            deltas[field_path] = float(wls_value) - float(row_value)
    return dict(sorted(deltas.items()))


def _collapse_learning_probe_report(
    lanes: Sequence[GRCL9V3ReplayLaneResult],
) -> Mapping[str, Any]:
    lane_summaries = [_collapse_learning_lane_summary(lane) for lane in lanes]
    strong_lanes = [
        summary
        for summary in lane_summaries
        if summary["growth_before_collapse_observed"]
        and summary["learning_state_count"] > 0
        and summary["final_collapsed_sink_id"] is not None
    ]
    first_strong = min(
        strong_lanes,
        key=lambda summary: float(summary["lambda_birth"]),
        default=None,
    )
    runtime_grown_sink_lanes = [
        summary["fixture_name"]
        for summary in lane_summaries
        if summary["final_collapsed_sink_provenance"] == "runtime_grown"
    ]
    return {
        "report_version": "grcl9v3_collapse_learning_probe_report_v1",
        "probe_scope": (
            "runtime lambda_birth timing and sink-provenance probe over the "
            "delayed multi-center GRCL-9V3 source; not a new source ontology claim"
        ),
        "source_fixture": _COLLAPSE_LEARNING_PROBE_SOURCE,
        "requested_lambda_birth_values": [
            float(value) for _, value in _COLLAPSE_LEARNING_PROBE_LAMBDAS
        ],
        "lane_count": len(lane_summaries),
        "strong_growth_before_collapse_count": len(strong_lanes),
        "first_strong_lambda_birth": None
        if first_strong is None
        else float(first_strong["lambda_birth"]),
        "runtime_grown_sink_lanes": runtime_grown_sink_lanes,
        "lanes": lane_summaries,
    }


def _growth_collapse_relay_probe_report(
    lanes: Sequence[GRCL9V3ReplayLaneResult],
) -> Mapping[str, Any]:
    lane_summaries = [_growth_collapse_relay_lane_summary(lane) for lane in lanes]
    full_lanes = [
        summary
        for summary in lane_summaries
        if int(summary["full_growth_collapse_relay_count"]) > 0
    ]
    partial_lanes = [
        summary
        for summary in lane_summaries
        if int(summary["growth_child_later_collapsed_sink_count"]) > 0
        or int(summary["collapsed_sink_later_growth_parent_count"]) > 0
    ]
    return {
        "report_version": "grcl9v3_growth_collapse_relay_probe_report_v1",
        "probe_scope": (
            "runtime recurrent relay diagnostic over the delayed multi-center "
            "GRCL-9V3 source. Full relay requires the same runtime node to "
            "appear as growth child, later collapsed sink, and later growth parent."
        ),
        "source_fixture": _COLLAPSE_LEARNING_PROBE_SOURCE,
        "lane_count": len(lane_summaries),
        "partial_relay_lane_count": len(partial_lanes),
        "full_relay_lane_count": len(full_lanes),
        "full_relay_found": bool(full_lanes),
        "lanes": lane_summaries,
    }


def _relay_port_probe_report(
    lanes: Sequence[GRCL9V3ReplayLaneResult],
) -> Mapping[str, Any]:
    lane_summaries = [_growth_collapse_relay_lane_summary(lane) for lane in lanes]
    full_lanes = [
        summary
        for summary in lane_summaries
        if int(summary["full_growth_collapse_relay_count"]) > 0
    ]
    partial_lanes = [
        summary
        for summary in lane_summaries
        if int(summary["growth_child_later_collapsed_sink_count"]) > 0
        or int(summary["collapsed_sink_later_growth_parent_count"]) > 0
    ]
    return {
        "report_version": "grcl9v3_relay_port_probe_report_v1",
        "probe_scope": (
            "runtime relay-port geometry diagnostic over the delayed "
            "multi-center GRCL-9V3 source. The source declares a birth-port "
            "scaffold with calibrated support and a weak outlet; full relay "
            "still requires same-node growth-child -> collapsed-sink -> "
            "growth-parent evidence."
        ),
        "source_fixture": _COLLAPSE_LEARNING_PROBE_SOURCE,
        "lane_count": len(lane_summaries),
        "partial_relay_lane_count": len(partial_lanes),
        "full_relay_lane_count": len(full_lanes),
        "full_relay_found": bool(full_lanes),
        "lanes": lane_summaries,
    }


def _growth_collapse_relay_lane_summary(
    lane: GRCL9V3ReplayLaneResult,
) -> Mapping[str, Any]:
    base_summary = dict(_collapse_learning_lane_summary(lane))
    events = _read_jsonl(Path(lane.artifact_root) / "telemetry" / "events.jsonl")
    relay = _relay_role_summary(events)
    base_summary.update(relay)
    return base_summary


def _relay_role_summary(events: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    first_growth_child: dict[str, tuple[int, int]] = {}
    first_growth_parent: dict[str, tuple[int, int]] = {}
    first_collapsed_sink: dict[str, tuple[int, int]] = {}
    for event in events:
        event_index = int(event.get("event_index", -1))
        step_index = int(event.get("step_index", -1))
        event_kind = str(event.get("event_kind", ""))
        if event_kind == "growth":
            child_id = _path_value(event, "payload.child_node_id")
            parent_id = _path_value(event, "payload.parent_node_id")
            if child_id is not None:
                first_growth_child.setdefault(str(child_id), (event_index, step_index))
            if parent_id is not None:
                first_growth_parent.setdefault(str(parent_id), (event_index, step_index))
        elif event_kind == "collapse":
            sink_id = _path_value(event, "payload.collapsed_sink_id")
            if sink_id is not None:
                first_collapsed_sink.setdefault(str(sink_id), (event_index, step_index))

    child_later_sink = []
    sink_later_parent = []
    full_relay = []
    for node_id, (child_event, child_step) in sorted(first_growth_child.items()):
        collapse = first_collapsed_sink.get(node_id)
        parent = first_growth_parent.get(node_id)
        if collapse is not None and _event_after(collapse, (child_event, child_step)):
            child_later_sink.append(
                {
                    "node_id": node_id,
                    "growth_child_event_index": child_event,
                    "growth_child_step_index": child_step,
                    "collapse_event_index": collapse[0],
                    "collapse_step_index": collapse[1],
                }
            )
            if parent is not None and _event_after(parent, collapse):
                full_relay.append(
                    {
                        "node_id": node_id,
                        "growth_child_event_index": child_event,
                        "growth_child_step_index": child_step,
                        "collapse_event_index": collapse[0],
                        "collapse_step_index": collapse[1],
                        "growth_parent_event_index": parent[0],
                        "growth_parent_step_index": parent[1],
                    }
                )
    for node_id, (collapse_event, collapse_step) in sorted(first_collapsed_sink.items()):
        parent = first_growth_parent.get(node_id)
        if parent is not None and _event_after(parent, (collapse_event, collapse_step)):
            sink_later_parent.append(
                {
                    "node_id": node_id,
                    "collapse_event_index": collapse_event,
                    "collapse_step_index": collapse_step,
                    "growth_parent_event_index": parent[0],
                    "growth_parent_step_index": parent[1],
                }
            )
    return {
        "growth_child_later_collapsed_sink_count": len(child_later_sink),
        "collapsed_sink_later_growth_parent_count": len(sink_later_parent),
        "full_growth_collapse_relay_count": len(full_relay),
        "growth_child_later_collapsed_sink_sample": child_later_sink[:10],
        "collapsed_sink_later_growth_parent_sample": sink_later_parent[:10],
        "full_growth_collapse_relay_sample": full_relay[:10],
    }


def _event_after(
    right: tuple[int, int],
    left: tuple[int, int],
) -> bool:
    """Return true when right event occurs later by step, then event index."""

    right_event, right_step = right
    left_event, left_step = left
    return (right_step, right_event) > (left_step, left_event)


def _collapse_learning_lane_summary(
    lane: GRCL9V3ReplayLaneResult,
) -> Mapping[str, Any]:
    telemetry_root = Path(lane.artifact_root) / "telemetry"
    events = _read_jsonl(telemetry_root / "events.jsonl")
    summary = json.loads(
        (telemetry_root / "run_summary.json").read_text(encoding="utf-8")
    )
    lowered = json.loads(Path(lane.lowered_state_path).read_text(encoding="utf-8"))
    source = json.loads(Path(lane.source_fixture_path).read_text(encoding="utf-8"))
    lambda_birth = _collapse_learning_lambda_birth(source)
    first_growth = _first_event(events, "growth")
    first_collapse = _first_event(events, "collapse")
    first_collapse_after_growth = _first_event_after(
        events,
        "collapse",
        first_growth,
    )
    final_choice = _path_value(
        summary,
        "family_extensions.grc9v3.final_choice_collapse_summary",
    )
    final_choice = final_choice if isinstance(final_choice, Mapping) else {}
    final_sink = final_choice.get("last_collapsed_sink_id")
    final_sink_text = None if final_sink is None else str(final_sink)
    source_node_ids = {
        str(node_id)
        for node_id in (
            lowered.get("cached_quantities", {})
            .get("grcl9v3_provenance", {})
            .get("nodes", {})
            .keys()
        )
    }
    return {
        "fixture_name": lane.fixture_name,
        "lambda_birth": lambda_birth,
        "requested_steps": lane.requested_steps,
        "event_counts_by_kind": dict(lane.event_counts_by_kind),
        "first_growth_event_index": None
        if first_growth is None
        else int(first_growth["event_index"]),
        "first_growth_step_index": None
        if first_growth is None
        else int(first_growth["step_index"]),
        "first_collapse_event_index": None
        if first_collapse is None
        else int(first_collapse["event_index"]),
        "first_collapse_step_index": None
        if first_collapse is None
        else int(first_collapse["step_index"]),
        "first_collapse_after_growth_event_index": None
        if first_collapse_after_growth is None
        else int(first_collapse_after_growth["event_index"]),
        "first_collapse_after_growth_step_index": None
        if first_collapse_after_growth is None
        else int(first_collapse_after_growth["step_index"]),
        "growth_before_collapse_observed": first_growth is not None
        and first_collapse_after_growth is not None,
        "learning_state_count": int(final_choice.get("learning_state_count", 0) or 0),
        "collapse_registry_count": int(final_choice.get("collapse_registry_count", 0) or 0),
        "final_collapsed_sink_id": final_sink_text,
        "final_collapsed_sink_provenance": _sink_provenance(
            final_sink_text,
            source_node_ids=source_node_ids,
        ),
        "final_node_count": _path_value(
            summary,
            "family_extensions.grc9v3.final_port_chart_summary.num_nodes",
        ),
        "run_id": lane.run_id,
        "telemetry_root": str(telemetry_root),
    }


def _collapse_learning_lambda_birth(source: Mapping[str, Any]) -> float:
    notes = source.get("notes", {})
    if isinstance(notes, Mapping):
        value = notes.get("collapse_learning_probe_lambda_birth")
        if isinstance(value, int | float) and not isinstance(value, bool):
            return float(value)
        relay_overrides = notes.get("relay_port_probe_runtime_overrides")
        if isinstance(relay_overrides, Mapping):
            relay_value = relay_overrides.get("lambda_birth")
            if isinstance(relay_value, int | float) and not isinstance(relay_value, bool):
                return float(relay_value)
    for construct in source.get("constructs", ()):
        if not isinstance(construct, Mapping):
            continue
        if construct.get("construct_kind") != "growth_locus":
            continue
        value = construct.get("lambda_birth")
        if isinstance(value, int | float) and not isinstance(value, bool):
            return float(value)
    return 0.0


def _first_event(
    events: Sequence[Mapping[str, Any]],
    event_kind: str,
) -> Mapping[str, Any] | None:
    return next(
        (event for event in events if str(event.get("event_kind", "")) == event_kind),
        None,
    )


def _first_event_after(
    events: Sequence[Mapping[str, Any]],
    event_kind: str,
    previous_event: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    if previous_event is None:
        return None
    previous_order = (
        int(previous_event.get("event_index", -1)),
        int(previous_event.get("step_index", -1)),
    )
    return next(
        (
            event
            for event in events
            if str(event.get("event_kind", "")) == event_kind
            and _event_after(
                (
                    int(event.get("event_index", -1)),
                    int(event.get("step_index", -1)),
                ),
                previous_order,
            )
        ),
        None,
    )


def _sink_provenance(
    sink_id: str | None,
    *,
    source_node_ids: set[str],
) -> str | None:
    if sink_id is None:
        return None
    if sink_id in source_node_ids:
        return "source_declared"
    return "runtime_grown"


def _series(steps: Sequence[Mapping[str, Any]], field_path: str) -> list[Any]:
    return [_path_value(step, field_path) for step in steps]


def _path_value(payload: Mapping[str, Any], field_path: str) -> Any:
    current: Any = payload
    for part in field_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def _read_jsonl(path: Path) -> tuple[Mapping[str, Any], ...]:
    return tuple(
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _control_role_for_source(source: GRCL9V3SourceDocument) -> str:
    if source.fixture_name.endswith("_positive_control"):
        return "positive_control"
    if source.fixture_name.endswith("_negative_control"):
        return "negative_control"
    if source.fixture_name.endswith("_no_event_control"):
        return "no_event_control"
    return "control"


def _module_node_ids(state: GRC9V3State) -> set[int]:
    module_node_ids: set[int] = set()
    for record in state.expansion_registry.values():
        module_node_ids.update(int(node_id) for node_id in record.module_node_ids)
    return module_node_ids


def _plain_json_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(canonicalize_json_value(payload), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replay GRCL-9V3 source fixtures through GRC9V3 telemetry."
    )
    parser.add_argument("--session-id", default="S0001")
    parser.add_argument("--output-root", default=str(GRCL9V3_REPLAY_ROOT))
    parser.add_argument("--steps", type=int, default=DEFAULT_REPLAY_STEPS)
    parser.add_argument(
        "--source-mode",
        choices=tuple(sorted(_SOURCE_MODES)),
        default="fixtures",
    )
    parser.add_argument(
        "--fixture",
        action="append",
        dest="fixtures",
        default=None,
        help="Fixture name to replay. Repeat to select multiple fixtures.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    result = run_grcl9v3_lowering_replay_session(
        session_id=args.session_id,
        output_root=Path(args.output_root),
        fixture_names=None if args.fixtures is None else tuple(args.fixtures),
        requested_steps=args.steps,
        source_mode=args.source_mode,
    )
    print(json.dumps(result.to_mapping(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_REPLAY_STEPS",
    "GRCL9V3_REPLAY_ROOT",
    "GRCL9V3_REPLAY_VERSION",
    "GRCL9V3ReplayLaneResult",
    "GRCL9V3ReplaySessionResult",
    "run_grcl9v3_lowering_replay_session",
]
