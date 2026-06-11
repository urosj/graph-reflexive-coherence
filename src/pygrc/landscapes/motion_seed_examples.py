"""Authored motion seed examples and composite motion sessions."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pygrc.core import canonical_json_dumps, canonicalize_json_value
from pygrc.telemetry.schema import (
    EventTelemetryRow,
    GraphCheckpointArtifact,
    RunTelemetryIdentity,
)

from .io import save_landscape_seed
from .seed import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapeSeed,
    RidgeSeedPrimitive,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedGeometryHints,
    SeedPotential,
    SeedTransportIntent,
    ValleySeedPrimitive,
)
from . import motion_examples as _runtime_examples
from .motion_examples import MotionStructuralExampleRun, MotionStructuralExampleSpec


MOTION_SEED_EXAMPLES_SESSION_VERSION = "motion_seed_examples_iter10_v1"
MOTION_LONG_COMPOSITES_SESSION_VERSION = "motion_long_composites_iter11_v1"
MOTION_DENSE_FISSION_SESSION_VERSION = "motion_dense_fission_iter12_5_v1"
MOTION_SEED_EXTENSION_VERSION = "motion_seed.v1"
DEFAULT_MOTION_SEED_OUTPUT_ROOT = Path("outputs/motion")
DEFAULT_MOTION_SEED_SESSION_ID = "S0002"
DEFAULT_MOTION_LONG_COMPOSITE_SESSION_ID = "S0003"
DEFAULT_MOTION_DENSE_FISSION_SESSION_ID = "S0005"
DEFAULT_MOTION_SEED_LIBRARY_DIR = Path("configs/landscapes/seed/motion")
DEFAULT_DENSE_FISSION_PARENT_COUNT = 501

_NON_CLAIMS = (
    "source_preconditions_only",
    "no_runtime_motion_claim",
    "no_motion_record_claim",
    "no_solved_checkpoint_claim",
)
_FORBIDDEN_SOURCE_KEYS = frozenset(
    {
        "motion_id",
        "motion_record",
        "motion_records",
        "relationship",
        "observed_motion",
        "runtime_motion",
        "checkpoint_ids",
        "step_rows",
        "event_rows",
        "graph_checkpoint",
        "transferred_mass",
    }
)


@dataclass(frozen=True)
class MotionAuthoredSeedSpec:
    """One authored source seed and its deterministic runtime projection."""

    seed_name: str
    runtime_family: str
    source_status: str
    seed: LandscapeSeed
    projected_examples: tuple[MotionStructuralExampleSpec, ...]
    notes: tuple[str, ...] = ()

    def to_mapping(self, *, seed_path: Path | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "seed_name": self.seed_name,
            "runtime_family": self.runtime_family,
            "source_status": self.source_status,
            "projected_example_names": [
                example.example_name for example in self.projected_examples
            ],
            "target_motion_modes": list(_target_motion_modes(self.seed)),
            "non_claims": list(_NON_CLAIMS),
            "notes": list(self.notes),
        }
        if seed_path is not None:
            payload["seed_path"] = str(seed_path)
        return canonicalize_json_value(payload)


@dataclass(frozen=True)
class MotionAuthoredSeedRun:
    """Persisted authored-seed projection result."""

    spec: MotionAuthoredSeedSpec
    library_seed_path: Path
    seed_path: Path
    projected_runs: tuple[MotionStructuralExampleRun, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                **self.spec.to_mapping(seed_path=self.seed_path),
                "library_seed_path": str(self.library_seed_path),
                "projected_runs": [run.to_mapping() for run in self.projected_runs],
                "observer_record_counts": _combined_counts(
                    run.observer_record_counts for run in self.projected_runs
                ),
                "observer_relationships": _combined_relationships(
                    run.observer_relationships for run in self.projected_runs
                ),
                "source_runtime_boundary": (
                    "source_seed_declares_preconditions_projected_runtime_evidence_drives_motion_records"
                ),
            }
        )


@dataclass(frozen=True)
class MotionSeedExamplesSession:
    """Iteration 10 authored-seed and composite motion session."""

    session_id: str
    session_root: Path
    runs: tuple[MotionAuthoredSeedRun, ...]
    visual_root: Path | None = None
    session_version: str = MOTION_SEED_EXAMPLES_SESSION_VERSION

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "session_version": self.session_version,
                "session_id": self.session_id,
                "session_root": str(self.session_root),
                "source_seed_count": len(self.runs),
                "projected_runtime_example_count": sum(
                    len(run.projected_runs) for run in self.runs
                ),
                "visual_root": None if self.visual_root is None else str(self.visual_root),
                "runs": [run.to_mapping() for run in self.runs],
            }
        )


def default_motion_authored_seed_specs() -> tuple[MotionAuthoredSeedSpec, ...]:
    """Return authored seed examples for Iteration 10."""

    base_examples = {
        spec.example_name: spec
        for spec in _runtime_examples.default_motion_structural_example_specs()
    }
    return (
        _authored_seed_spec(
            seed_name="motion_seed_coherence_transfer",
            runtime_family="grcv3",
            source_status="source_expressible_preconditions",
            target_motion_modes=("coherence",),
            projected_examples=(base_examples["coherence_transfer_control"],),
            primitives=(
                _basin("source_region", coherence=2.0, center=(0.0, 0.0)),
                _basin("target_region", coherence=0.5, center=(1.0, 0.0)),
                _valley("transfer_channel", "source_region", "target_region"),
            ),
            transport=(
                SeedTransportIntent(
                    id="coherence_pressure_intent",
                    mode="directed_flux_precondition",
                    sources=["source_region"],
                    targets=["target_region"],
                    magnitude_hint=1.0,
                    carrier_id="transfer_channel",
                    notes="Source declares flux precondition only; transfer is observed after runtime projection.",
                ),
            ),
        ),
        _authored_seed_spec(
            seed_name="motion_seed_representative_drift",
            runtime_family="grcv3",
            source_status="source_expressible_preconditions",
            target_motion_modes=("representative",),
            projected_examples=(base_examples["representative_drift_control"],),
            primitives=(
                _basin("basin_alpha", coherence=2.0, center=(0.0, 0.0)),
                _basin("basin_alpha_neighbor", coherence=0.5, center=(1.0, 0.0)),
                _ridge("soft_internal_ridge", adjacent=("basin_alpha", "basin_alpha_neighbor")),
            ),
            transport=(),
        ),
        _authored_seed_spec(
            seed_name="motion_seed_identity_walking",
            runtime_family="grc9v3",
            source_status="partial_source_expressible_continuity_preconditions",
            target_motion_modes=("identity",),
            projected_examples=(base_examples["identity_walking_control"],),
            primitives=(
                _basin("old_identity_basin", coherence=2.0, center=(0.0, 0.0)),
                _basin("new_identity_basin", coherence=2.0, center=(1.0, 0.0)),
                _valley("identity_continuity_channel", "old_identity_basin", "new_identity_basin"),
            ),
            transport=(
                SeedTransportIntent(
                    id="successor_continuity_intent",
                    mode="successor_and_flux_precondition",
                    sources=["old_identity_basin"],
                    targets=["new_identity_basin"],
                    magnitude_hint=1.0,
                    carrier_id="identity_continuity_channel",
                ),
            ),
            notes=(
                "Identity walking is not source-claimed; source expresses continuity preconditions only.",
            ),
        ),
        _authored_seed_spec(
            seed_name="motion_seed_grc9_port_frontier",
            runtime_family="grc9",
            source_status="source_expressible_preconditions",
            target_motion_modes=("boundary",),
            projected_examples=(base_examples["grc9_port_frontier_motion"],),
            primitives=(
                _basin("frontier_parent", coherence=1.0, center=(0.0, 0.0)),
                _junction("frontier_port_locus", host="frontier_parent"),
            ),
            transport=(),
        ),
        _authored_seed_spec(
            seed_name="motion_seed_grc9v3_hybrid_refinement",
            runtime_family="grc9v3",
            source_status="source_expressible_hybrid_preconditions",
            target_motion_modes=("boundary", "topological"),
            projected_examples=(base_examples["grc9v3_hybrid_refinement_motion"],),
            primitives=(
                _basin("saturated_parent", coherence=2.0, center=(0.0, 0.0)),
                _junction("hybrid_refinement_locus", host="saturated_parent"),
            ),
            transport=(),
        ),
        _authored_seed_spec(
            seed_name="motion_composite_walk_frontier_refinement",
            runtime_family="grc9v3",
            source_status="composite_projected_runtime_evidence",
            target_motion_modes=("identity", "boundary", "topological"),
            projected_examples=(_composite_walk_frontier_refinement(),),
            primitives=(
                _basin("walking_origin", coherence=2.0, center=(0.0, 0.0)),
                _basin("walking_successor", coherence=2.0, center=(1.0, 0.0)),
                _junction("frontier_refinement_locus", host="walking_successor"),
                _valley("walking_channel", "walking_origin", "walking_successor"),
            ),
            transport=(
                SeedTransportIntent(
                    id="walking_then_refinement_intent",
                    mode="ordered_precondition_sequence",
                    sources=["walking_origin"],
                    targets=["walking_successor"],
                    magnitude_hint=1.0,
                    carrier_id="walking_channel",
                ),
            ),
        ),
        _authored_seed_spec(
            seed_name="motion_composite_split_merge_collapse",
            runtime_family="grc9v3",
            source_status="composite_projected_runtime_evidence",
            target_motion_modes=("identity", "topological"),
            projected_examples=(_composite_split_merge_collapse(),),
            primitives=(
                _basin("composite_parent", coherence=2.0, center=(0.0, 0.0)),
                _basin("composite_child_a", coherence=1.0, center=(-0.5, 1.0)),
                _basin("composite_child_b", coherence=1.0, center=(0.5, 1.0)),
                _basin("composite_merge_sink", coherence=2.0, center=(0.0, 2.0)),
                _basin("composite_collapse_sink", coherence=0.5, center=(0.0, 3.0)),
            ),
            transport=(),
        ),
    )


def default_motion_long_composite_seed_specs() -> tuple[MotionAuthoredSeedSpec, ...]:
    """Return long-window authored composite seeds for Iteration 11."""

    return (
        _authored_seed_spec(
            seed_name="motion_long_relay_walk_frontier",
            runtime_family="grc9v3",
            source_status="long_window_composite_projected_runtime_evidence",
            target_motion_modes=("identity", "boundary", "topological"),
            projected_examples=(_long_relay_walk_frontier(),),
            primitives=(
                _basin("relay_origin", coherence=2.0, center=(0.0, 0.0)),
                _basin("relay_mid_a", coherence=2.0, center=(1.0, 0.0)),
                _basin("relay_mid_b", coherence=2.0, center=(2.0, 0.0)),
                _basin("relay_mid_c", coherence=2.0, center=(3.0, 0.0)),
                _basin("relay_terminal", coherence=2.0, center=(4.0, 0.0)),
                _valley("relay_channel_0", "relay_origin", "relay_mid_a"),
                _valley("relay_channel_1", "relay_mid_a", "relay_mid_b"),
                _valley("relay_channel_2", "relay_mid_b", "relay_mid_c"),
                _valley("relay_channel_3", "relay_mid_c", "relay_terminal"),
                _junction("relay_frontier_locus", host="relay_terminal"),
            ),
            transport=(
                SeedTransportIntent(
                    id="long_relay_continuity_intent",
                    mode="delayed_successor_flux_precondition",
                    sources=["relay_origin"],
                    targets=["relay_terminal"],
                    magnitude_hint=1.0,
                    notes="Long-window relay preconditions; observed walking is inferred from checkpoints.",
                ),
            ),
            notes=("Twenty-one checkpoint relay with delayed identity walks and frontier advances.",),
        ),
        _authored_seed_spec(
            seed_name="motion_long_split_merge_collapse_cascade",
            runtime_family="grc9v3",
            source_status="long_window_composite_projected_runtime_evidence",
            target_motion_modes=("identity", "boundary", "topological"),
            projected_examples=(_long_split_merge_collapse_cascade(),),
            primitives=(
                _basin("cascade_parent", coherence=2.0, center=(0.0, 0.0)),
                _basin("cascade_child_a", coherence=1.0, center=(-0.75, 1.0)),
                _basin("cascade_child_b", coherence=1.0, center=(0.75, 1.0)),
                _basin("cascade_merge_sink", coherence=2.0, center=(0.0, 2.0)),
                _basin("cascade_collapse_sink", coherence=0.5, center=(0.0, 3.0)),
                _junction("cascade_frontier_locus", host="cascade_merge_sink"),
            ),
            transport=(
                SeedTransportIntent(
                    id="long_cascade_topology_intent",
                    mode="delayed_split_merge_collapse_precondition",
                    sources=["cascade_parent"],
                    targets=["cascade_collapse_sink"],
                    magnitude_hint=1.0,
                ),
            ),
            notes=("Twenty-four checkpoint cascade with delayed split, merge, and collapse.",),
        ),
        _authored_seed_spec(
            seed_name="motion_long_failed_relay_broken_continuity",
            runtime_family="grc9v3",
            source_status="long_window_failed_composite_projected_runtime_evidence",
            target_motion_modes=("identity", "topological"),
            projected_examples=(_long_failed_relay_broken_continuity(),),
            primitives=(
                _basin("failed_relay_origin", coherence=2.0, center=(0.0, 0.0)),
                _basin("failed_relay_terminal", coherence=2.0, center=(4.0, 0.0)),
                _valley("failed_relay_missing_channel", "failed_relay_origin", "failed_relay_terminal"),
            ),
            transport=(
                SeedTransportIntent(
                    id="failed_relay_continuity_intent",
                    mode="insufficient_successor_flux_precondition",
                    sources=["failed_relay_origin"],
                    targets=["failed_relay_terminal"],
                    magnitude_hint=0.0,
                    notes="Negative composite: source preconditions do not produce identity walking evidence.",
                ),
            ),
            notes=(
                "Twenty-one checkpoint failed relay; records why a source-level relay can remain dissolved/emerged instead of walked.",
            ),
        ),
        _authored_seed_spec(
            seed_name="motion_long_no_motion_negative_control",
            runtime_family="grc9v3",
            source_status="long_window_negative_control_projected_runtime_evidence",
            target_motion_modes=("identity", "boundary", "topological"),
            projected_examples=(_long_no_motion_negative_control(),),
            primitives=(
                _basin("stable_identity", coherence=2.0, center=(0.0, 0.0)),
                _junction("stable_frontier_locus", host="stable_identity"),
            ),
            transport=(),
            notes=("Twenty-one checkpoint stable negative control; non-stationary motion should stay absent.",),
        ),
    )


def default_motion_dense_fission_seed_specs() -> tuple[MotionAuthoredSeedSpec, ...]:
    """Return dense confirmed-fission authored seed for Iteration 12.5."""

    return (
        _authored_seed_spec(
            seed_name="motion_dense_confirmed_fission",
            runtime_family="grc9v3",
            source_status="dense_confirmed_fission_projected_runtime_evidence",
            target_motion_modes=("identity", "topological"),
            projected_examples=(_dense_confirmed_fission_composition(),),
            primitives=(
                _basin("dense_fission_parent_template", coherence=4.0, center=(0.0, 0.0)),
                _basin("dense_fission_daughter_a_template", coherence=2.0, center=(-0.5, 1.0)),
                _basin("dense_fission_daughter_b_template", coherence=2.0, center=(0.5, 1.0)),
                _valley(
                    "dense_fission_provenance_channel_a",
                    "dense_fission_parent_template",
                    "dense_fission_daughter_a_template",
                ),
                _valley(
                    "dense_fission_provenance_channel_b",
                    "dense_fission_parent_template",
                    "dense_fission_daughter_b_template",
                ),
            ),
            transport=(
                SeedTransportIntent(
                    id="dense_compact_fission_intent",
                    mode="compact_daughter_provenance_precondition",
                    sources=["dense_fission_parent_template"],
                    targets=[
                        "dense_fission_daughter_a_template",
                        "dense_fission_daughter_b_template",
                    ],
                    magnitude_hint=1.0,
                    notes=(
                        "Source declares repeated compact parent/daughter preconditions; "
                        "identity fission is accepted only if observed promotion gates pass."
                    ),
                ),
            ),
            notes=(
                "Iteration 12.5 dense session designed to produce promotion-grade compact fission evidence.",
            ),
        ),
    )


def run_motion_authored_seed_examples(
    *,
    output_root: str | Path = DEFAULT_MOTION_SEED_OUTPUT_ROOT,
    session_id: str = DEFAULT_MOTION_SEED_SESSION_ID,
    seed_names: Sequence[str] | None = None,
    render_visuals: bool = True,
    seed_library_dir: str | Path = DEFAULT_MOTION_SEED_LIBRARY_DIR,
) -> MotionSeedExamplesSession:
    """Write authored seeds, project them to runtime evidence, and run observers."""

    return _run_motion_seed_specs(
        specs=default_motion_authored_seed_specs(),
        output_root=output_root,
        session_id=session_id,
        seed_names=seed_names,
        render_visuals=render_visuals,
        seed_library_dir=seed_library_dir,
        session_version=MOTION_SEED_EXAMPLES_SESSION_VERSION,
    )


def run_motion_long_composite_examples(
    *,
    output_root: str | Path = DEFAULT_MOTION_SEED_OUTPUT_ROOT,
    session_id: str = DEFAULT_MOTION_LONG_COMPOSITE_SESSION_ID,
    seed_names: Sequence[str] | None = None,
    render_visuals: bool = True,
    seed_library_dir: str | Path = DEFAULT_MOTION_SEED_LIBRARY_DIR,
) -> MotionSeedExamplesSession:
    """Run long-window authored composite projections for Iteration 11."""

    return _run_motion_seed_specs(
        specs=default_motion_long_composite_seed_specs(),
        output_root=output_root,
        session_id=session_id,
        seed_names=seed_names,
        render_visuals=render_visuals,
        seed_library_dir=seed_library_dir,
        session_version=MOTION_LONG_COMPOSITES_SESSION_VERSION,
    )


def run_motion_dense_fission_examples(
    *,
    output_root: str | Path = DEFAULT_MOTION_SEED_OUTPUT_ROOT,
    session_id: str = DEFAULT_MOTION_DENSE_FISSION_SESSION_ID,
    seed_names: Sequence[str] | None = None,
    render_visuals: bool = False,
    seed_library_dir: str | Path = DEFAULT_MOTION_SEED_LIBRARY_DIR,
) -> MotionSeedExamplesSession:
    """Run dense confirmed-fission authored seed projections for Iteration 12.5."""

    return _run_motion_seed_specs(
        specs=default_motion_dense_fission_seed_specs(),
        output_root=output_root,
        session_id=session_id,
        seed_names=seed_names,
        render_visuals=render_visuals,
        seed_library_dir=seed_library_dir,
        session_version=MOTION_DENSE_FISSION_SESSION_VERSION,
    )


def _run_motion_seed_specs(
    *,
    specs: Sequence[MotionAuthoredSeedSpec],
    output_root: str | Path,
    session_id: str,
    seed_names: Sequence[str] | None,
    render_visuals: bool,
    seed_library_dir: str | Path,
    session_version: str,
) -> MotionSeedExamplesSession:
    """Shared authored-seed session runner."""

    root = Path(output_root)
    session_root = root / "sessions" / session_id
    source_seed_dir = session_root / "source_seeds"
    source_seed_dir.mkdir(parents=True, exist_ok=True)
    library_dir = Path(seed_library_dir)
    library_dir.mkdir(parents=True, exist_ok=True)
    selected = _select_seed_specs(specs, seed_names)

    runs: list[MotionAuthoredSeedRun] = []
    for spec in selected:
        _validate_no_runtime_motion_smuggling(spec.seed.extensions, context=spec.seed_name)
        library_seed_path = library_dir / f"{spec.seed_name}.seed.yaml"
        save_landscape_seed(spec.seed, library_seed_path)
        seed_path = source_seed_dir / f"{spec.seed_name}.seed.json"
        save_landscape_seed(spec.seed, seed_path)
        projected_runs = tuple(
            _runtime_examples._run_example(session_root, projected)
            for projected in spec.projected_examples
        )
        runs.append(
            MotionAuthoredSeedRun(
                spec=spec,
                library_seed_path=library_seed_path,
                seed_path=seed_path,
                projected_runs=projected_runs,
            )
        )

    session = MotionSeedExamplesSession(
        session_id=session_id,
        session_root=session_root,
        runs=tuple(runs),
        session_version=session_version,
    )
    _write_json(session_root / "session_manifest.json", _session_manifest(session))
    _write_json(session_root / "run_report.json", session.to_mapping())
    _write_json(session_root / "landscape_motion_summary.json", _seed_motion_summary(session))
    _write_text(session_root / "README.md", _readme(session))
    _write_text(
        session_root / "rerun.sh",
        _rerun_script(
            root,
            session_id,
            seed_names,
            long_composites=session_version == MOTION_LONG_COMPOSITES_SESSION_VERSION,
            dense_fission=session_version == MOTION_DENSE_FISSION_SESSION_VERSION,
        ),
    )
    if render_visuals:
        from pygrc.visualization.motion import render_motion_visual_session

        visual_session = render_motion_visual_session(session_root=session_root)
        session = MotionSeedExamplesSession(
            session_id=session_id,
            session_root=session_root,
            runs=tuple(runs),
            visual_root=visual_session.visual_root,
            session_version=session_version,
        )
        _write_json(session_root / "run_report.json", session.to_mapping())
        _write_json(session_root / "landscape_motion_summary.json", _seed_motion_summary(session))
    return session


def _authored_seed_spec(
    *,
    seed_name: str,
    runtime_family: str,
    source_status: str,
    target_motion_modes: tuple[str, ...],
    projected_examples: tuple[MotionStructuralExampleSpec, ...],
    primitives: tuple[Any, ...],
    transport: tuple[SeedTransportIntent, ...],
    notes: tuple[str, ...] = (),
) -> MotionAuthoredSeedSpec:
    seed = LandscapeSeed(
        seed_schema="pygrc.landscape_seed.v1",
        seed_version="motion_seed_iter10_v1",
        meta=SeedDocumentMeta(
            name=seed_name,
            source_kind="authored_motion_seed",
            source_reference="implementation/Motion-ImplementationPlan.md#iteration-10",
            source_schema_version=MOTION_SEED_EXTENSION_VERSION,
            source_domain="motion_inference",
            description=f"Authored preconditions for {', '.join(target_motion_modes)} motion review.",
            tags=["motion", "iteration_10", runtime_family],
            translator_name="motion_seed_examples",
            translator_version=MOTION_SEED_EXAMPLES_SESSION_VERSION,
            translation_mode="semantic_enrichment",
            translation_notes=list(_NON_CLAIMS),
        ),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=1.0,
            kappa_c=1.0,
            dt=0.1,
            potential=SeedPotential(type="motion_source_precondition", params={}),
            notes="Authoring profile for runtime projection tests; not a solved motion outcome.",
        ),
        primitives=list(primitives),
        transport_intent=list(transport),
        geometry_hints=SeedGeometryHints(source_chart="motion_iter10_source_chart"),
        extensions={
            "motion_seed": {
                "contract_version": MOTION_SEED_EXTENSION_VERSION,
                "runtime_family": runtime_family,
                "source_status": source_status,
                "target_motion_modes": list(target_motion_modes),
                "projected_example_names": [
                    example.example_name for example in projected_examples
                ],
                "non_claims": list(_NON_CLAIMS),
                "notes": list(notes),
            }
        },
    )
    return MotionAuthoredSeedSpec(
        seed_name=seed_name,
        runtime_family=runtime_family,
        source_status=source_status,
        seed=seed,
        projected_examples=projected_examples,
        notes=notes,
    )


def _basin(name: str, *, coherence: float, center: tuple[float, float]) -> BasinSeedPrimitive:
    return BasinSeedPrimitive(
        id=name,
        label=name.replace("_", " "),
        role="motion_source_region",
        coherence_prior=coherence,
        chart_center_hint=[float(center[0]), float(center[1])],
        extensions={"motion_seed": {"source_role": "precondition_region"}},
    )


def _ridge(name: str, *, adjacent: tuple[str, ...]) -> RidgeSeedPrimitive:
    return RidgeSeedPrimitive(
        id=name,
        label=name.replace("_", " "),
        role="motion_source_separator",
        adjacent_ids=list(adjacent),
        extensions={"motion_seed": {"source_role": "boundary_precondition"}},
    )


def _valley(name: str, source: str, target: str) -> ValleySeedPrimitive:
    return ValleySeedPrimitive(
        id=name,
        label=name.replace("_", " "),
        role="motion_source_channel",
        from_id=source,
        to_id=target,
        channel_role="transport_precondition",
        extensions={"motion_seed": {"source_role": "flux_path_precondition"}},
    )


def _junction(name: str, *, host: str) -> JunctionSeedPrimitive:
    return JunctionSeedPrimitive(
        id=name,
        label=name.replace("_", " "),
        role="motion_source_junction",
        host_id=host,
        junction_role="frontier_or_refinement_precondition",
        extensions={"motion_seed": {"source_role": "topology_precondition"}},
    )


def _composite_walk_frontier_refinement() -> MotionStructuralExampleSpec:
    identity = _identity("motion_composite_walk_frontier_refinement", "grc9v3", 3)
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
                    "basin_id": "basin_origin",
                    "is_sink": True,
                    "occupied_ports": [1, 2],
                    "payload": {
                        "successor_node_id": 2,
                        "hierarchy_parent": "motion_parent",
                        "source_construct_id": "composite_walk",
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
                    "basin_id": "basin_successor",
                    "is_sink": True,
                    "occupied_ports": [1, 2],
                    "payload": {
                        "hierarchy_parent": "motion_parent",
                        "source_construct_id": "composite_walk",
                    },
                },
            ),
            edges=({"edge_id": 12, "source_node_id": 1, "target_node_id": 2, "signed_flux": 1.0},),
        ),
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0002",
            step_index=2,
            nodes=(
                {
                    "node_id": 2,
                    "coherence": 1.5,
                    "basin_id": "basin_successor",
                    "is_sink": True,
                    "occupied_ports": [1, 2, 3],
                    "payload": {"source_construct_id": "composite_walk"},
                },
                {"node_id": 3, "coherence": 0.5, "basin_id": "basin_child", "occupied_ports": [1]},
            ),
            edges=({"edge_id": 23, "source_node_id": 2, "target_node_id": 3, "signed_flux": 0.5},),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="motion_composite_walk_frontier_refinement",
        runtime_family="grc9v3",
        purpose="Composite runtime projection: identity walking followed by frontier/topology refinement.",
        evidence_scale="authored_seed_projection",
        checkpoints=checkpoints,
        events=(
            _event(identity, "grc9v3", "hybrid_mechanical_expansion", payload={"node_id": 2}, step_index=2),
        ),
        observers=("identity", "boundary", "topological"),
        expected_record_kinds=("identity", "boundary", "topological"),
        notes=("Projected from source preconditions; motion relationship is observer-inferred.",),
    )


def _composite_split_merge_collapse() -> MotionStructuralExampleSpec:
    identity = _identity("motion_composite_split_merge_collapse", "grc9v3", 4)
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
                {"edge_id": 24, "source_node_id": 2, "target_node_id": 4, "signed_flux": 1.0},
                {"edge_id": 34, "source_node_id": 3, "target_node_id": 4, "signed_flux": 1.0},
            ),
        ),
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0002",
            step_index=2,
            nodes=({"node_id": 4, "coherence": 2.0, "basin_id": "basin_merged", "is_sink": True},),
            edges=({"edge_id": 45, "source_node_id": 4, "target_node_id": 5, "signed_flux": 1.0},),
        ),
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id="checkpoint_0003",
            step_index=3,
            nodes=({"node_id": 5, "coherence": 0.5, "basin_id": "basin_collapsed", "is_sink": True},),
            edges=({"edge_id": 45, "source_node_id": 4, "target_node_id": 5, "signed_flux": 1.0},),
        ),
    )
    return MotionStructuralExampleSpec(
        example_name="motion_composite_split_merge_collapse",
        runtime_family="grc9v3",
        purpose="Composite runtime projection with split, merge, then collapse support changes.",
        evidence_scale="authored_seed_projection",
        checkpoints=checkpoints,
        events=(
            _event(identity, "grc9v3", "identity_fission", payload={"node_id": 1}, step_index=1),
            _event(identity, "grc9v3", "merge", payload={"node_id": 4}, step_index=2),
            _event(identity, "grc9v3", "collapse", payload={"node_id": 5}, step_index=3),
        ),
        observers=("identity", "topological"),
        expected_record_kinds=("identity", "topological"),
        notes=("Projected from source preconditions; topology sequence is observer/event backed.",),
    )


def _long_relay_walk_frontier() -> MotionStructuralExampleSpec:
    identity = _identity("motion_long_relay_walk_frontier", "grc9v3", 21)
    relay_nodes = (1, 2, 3, 4, 5)
    transition_steps = {5: 1, 10: 2, 15: 3, 20: 4}
    checkpoints: list[GraphCheckpointArtifact] = []
    for step in range(21):
        phase = min(step // 5, 4)
        node_id = relay_nodes[phase]
        basin_id = f"relay_basin_{phase}"
        occupied_count = min(9, 1 + (step % 5))
        payload: dict[str, object] = {
            "hierarchy_parent": "long_relay_parent",
            "source_construct_id": "long_relay_identity",
            "chart_center_hint": [float(phase), float((step % 5) * 0.1)],
        }
        edges: list[dict[str, object]] = []
        if step + 1 in transition_steps:
            successor = relay_nodes[transition_steps[step + 1]]
            payload["successor_node_id"] = successor
            edges.append(
                {
                    "edge_id": node_id * 10 + successor,
                    "source_node_id": node_id,
                    "target_node_id": successor,
                    "signed_flux": 1.0,
                }
            )
        checkpoints.append(
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id=f"checkpoint_{step:04d}",
                step_index=step,
                nodes=(
                    {
                        "node_id": node_id,
                        "coherence": 2.0,
                        "basin_id": basin_id,
                        "is_sink": True,
                        "occupied_ports": list(range(1, occupied_count + 1)),
                        "payload": payload,
                    },
                ),
                edges=tuple(edges),
            )
        )
    events = tuple(
        _event(
            identity,
            "grc9v3",
            "growth",
            payload={"node_id": relay_nodes[index]},
            step_index=step,
        )
        for step, index in sorted(transition_steps.items())
    )
    return MotionStructuralExampleSpec(
        example_name="motion_long_relay_walk_frontier",
        runtime_family="grc9v3",
        purpose="Twenty-one checkpoint relay: repeated delayed identity walking with frontier advances.",
        evidence_scale="long_window_authored_seed_projection",
        checkpoints=tuple(checkpoints),
        events=events,
        observers=("identity", "boundary", "topological"),
        expected_record_kinds=("identity", "boundary", "topological"),
        notes=("Long-window projection for Iteration 11 and animated visualization selection.",),
    )


def _long_split_merge_collapse_cascade() -> MotionStructuralExampleSpec:
    identity = _identity("motion_long_split_merge_collapse_cascade", "grc9v3", 24)
    checkpoints: list[GraphCheckpointArtifact] = []
    for step in range(24):
        if step < 6:
            payload = {
                "successor_node_id": 2 if step == 5 else None,
                "chart_center_hint": [0.0, float(step) * 0.05],
            }
            payload = {key: value for key, value in payload.items() if value is not None}
            nodes = (
                {
                    "node_id": 1,
                    "coherence": 2.0,
                    "basin_id": "cascade_parent",
                    "is_sink": True,
                    "occupied_ports": list(range(1, min(9, step + 2) + 1)),
                    "payload": payload,
                },
            )
            edges = (
                {"edge_id": 12, "source_node_id": 1, "target_node_id": 2, "signed_flux": 1.0},
                {"edge_id": 13, "source_node_id": 1, "target_node_id": 3, "signed_flux": 1.0},
            ) if step == 5 else ()
        elif step < 13:
            ports = list(range(1, min(9, (step - 5) + 1) + 1))
            nodes = (
                {
                    "node_id": 2,
                    "coherence": 1.0,
                    "basin_id": "cascade_child_a",
                    "is_sink": True,
                    "occupied_ports": ports,
                    "payload": {"chart_center_hint": [-0.75, 1.0 + (step - 6) * 0.05]},
                },
                {
                    "node_id": 3,
                    "coherence": 1.0,
                    "basin_id": "cascade_child_b",
                    "is_sink": True,
                    "occupied_ports": ports,
                    "payload": {"chart_center_hint": [0.75, 1.0 + (step - 6) * 0.05]},
                },
            )
            edges = (
                {"edge_id": 24, "source_node_id": 2, "target_node_id": 4, "signed_flux": 1.0},
                {"edge_id": 34, "source_node_id": 3, "target_node_id": 4, "signed_flux": 1.0},
            ) if step == 12 else ()
        elif step < 20:
            nodes = (
                {
                    "node_id": 4,
                    "coherence": 2.0,
                    "basin_id": "cascade_merged",
                    "is_sink": True,
                    "occupied_ports": list(range(1, min(9, (step - 12) + 1) + 1)),
                    "payload": {"chart_center_hint": [0.0, 2.0 + (step - 13) * 0.05]},
                },
            )
            edges = (
                {"edge_id": 45, "source_node_id": 4, "target_node_id": 5, "signed_flux": 1.0},
            ) if step == 19 else ()
        else:
            nodes = (
                {
                    "node_id": 5,
                    "coherence": 0.5,
                    "basin_id": "cascade_collapsed",
                    "is_sink": True,
                    "occupied_ports": [1],
                    "payload": {"chart_center_hint": [0.0, 3.0 + (step - 20) * 0.05]},
                },
            )
            edges = ()
        checkpoints.append(
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id=f"checkpoint_{step:04d}",
                step_index=step,
                nodes=nodes,
                edges=edges,
            )
        )
    return MotionStructuralExampleSpec(
        example_name="motion_long_split_merge_collapse_cascade",
        runtime_family="grc9v3",
        purpose="Twenty-four checkpoint cascade: delayed split, merge, frontier changes, and collapse.",
        evidence_scale="long_window_authored_seed_projection",
        checkpoints=tuple(checkpoints),
        events=(
            _event(identity, "grc9v3", "identity_fission", payload={"node_id": 1}, step_index=6),
            _event(identity, "grc9v3", "merge", payload={"node_id": 4}, step_index=13),
            _event(identity, "grc9v3", "collapse", payload={"node_id": 5}, step_index=20),
        ),
        observers=("identity", "boundary", "topological"),
        expected_record_kinds=("identity", "boundary", "topological"),
        notes=("Long-window projection preserves identity/topology disagreement around collapse.",),
    )


def _long_failed_relay_broken_continuity() -> MotionStructuralExampleSpec:
    identity = _identity("motion_long_failed_relay_broken_continuity", "grc9v3", 21)
    checkpoints: list[GraphCheckpointArtifact] = []
    for step in range(21):
        if step < 10:
            nodes = (
                {
                    "node_id": 1,
                    "coherence": 2.0,
                    "basin_id": "failed_relay_origin",
                    "is_sink": True,
                    "occupied_ports": [1, 2],
                    "payload": {
                        "hierarchy_parent": "failed_relay_parent_a",
                        "source_construct_id": "failed_relay_origin_construct",
                        "chart_center_hint": [0.0, float(step) * 0.02],
                    },
                },
            )
        else:
            nodes = (
                {
                    "node_id": 5,
                    "coherence": 2.0,
                    "basin_id": "failed_relay_terminal",
                    "is_sink": True,
                    "occupied_ports": [1, 2],
                    "payload": {
                        "hierarchy_parent": "failed_relay_parent_b",
                        "source_construct_id": "failed_relay_terminal_construct",
                        "chart_center_hint": [4.0, float(step - 10) * 0.02],
                    },
                },
            )
        checkpoints.append(
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id=f"checkpoint_{step:04d}",
                step_index=step,
                nodes=nodes,
                edges=(),
            )
        )
    return MotionStructuralExampleSpec(
        example_name="motion_long_failed_relay_broken_continuity",
        runtime_family="grc9v3",
        purpose="Twenty-one checkpoint negative relay: source-like endpoints exist but continuity evidence is broken.",
        evidence_scale="long_window_failed_authored_seed_projection",
        checkpoints=tuple(checkpoints),
        events=(),
        observers=("identity", "topological"),
        expected_record_kinds=("identity", "topological"),
        negative_control=True,
        notes=(
            "No successor, flux path, or provenance continuity is provided across the endpoint handoff.",
        ),
    )


def _long_no_motion_negative_control() -> MotionStructuralExampleSpec:
    identity = _identity("motion_long_no_motion_negative_control", "grc9v3", 21)
    checkpoints = tuple(
        _checkpoint(
            identity,
            "grc9v3",
            checkpoint_id=f"checkpoint_{step:04d}",
            step_index=step,
            nodes=(
                {
                    "node_id": 1,
                    "coherence": 2.0,
                    "basin_id": "stable_identity",
                    "is_sink": True,
                    "occupied_ports": [1, 2, 3],
                    "payload": {
                        "hierarchy_parent": "stable_motion_parent",
                        "source_construct_id": "stable_identity_construct",
                        "chart_center_hint": [0.0, 0.0],
                    },
                },
            ),
            edges=(),
        )
        for step in range(21)
    )
    return MotionStructuralExampleSpec(
        example_name="motion_long_no_motion_negative_control",
        runtime_family="grc9v3",
        purpose="Twenty-one checkpoint negative control with stable support, frontier, and representative.",
        evidence_scale="long_window_negative_authored_seed_projection",
        checkpoints=checkpoints,
        events=(),
        observers=("identity", "representative", "boundary", "topological"),
        expected_record_kinds=("identity",),
        negative_control=True,
        notes=("Stationary identity records are allowed; non-stationary motion should be absent.",),
    )


def _dense_confirmed_fission_composition(
    *,
    parent_count: int = DEFAULT_DENSE_FISSION_PARENT_COUNT,
) -> MotionStructuralExampleSpec:
    identity = _identity("motion_dense_confirmed_fission", "grc9v3", parent_count + 1)
    checkpoints: list[GraphCheckpointArtifact] = []
    events: list[EventTelemetryRow] = []
    for step in range(parent_count + 1):
        nodes: list[dict[str, object]] = []
        edges: list[dict[str, object]] = []
        if step > 0:
            previous_index = step - 1
            nodes.extend(_dense_fission_child_nodes(previous_index))
            edges.append(_dense_fission_edge(previous_index))
        if step < parent_count:
            nodes.extend(_dense_fission_parent_nodes(step))
            edges.append(_dense_fission_edge(step))
        checkpoints.append(
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id=f"checkpoint_{step:04d}",
                step_index=step,
                nodes=tuple(nodes),
                edges=tuple(edges),
            )
        )
    for index in range(parent_count):
        node_a = index * 10 + 1
        events.append(
            _event(
                identity,
                "grc9v3",
                "identity_fission",
                payload={"node_id": node_a, "parent_basin_id": f"dense_parent_{index:04d}"},
                step_index=index + 1,
            )
        )
    return MotionStructuralExampleSpec(
        example_name="motion_dense_confirmed_fission",
        runtime_family="grc9v3",
        purpose=(
            "Dense repetition of compact parent-to-two-daughter identity splits "
            "with provenance continuity for promotion-gate validation."
        ),
        evidence_scale="dense_confirmed_fission_seed_projection",
        checkpoints=tuple(checkpoints),
        events=tuple(events),
        observers=("identity", "topological"),
        expected_record_kinds=("identity", "topological"),
        notes=(
            f"{parent_count} compact fission motifs; raw records are still observer-inferred.",
        ),
    )


def _dense_fission_parent_nodes(index: int) -> tuple[dict[str, object], ...]:
    parent = f"dense_parent_{index:04d}"
    node_a = index * 10 + 1
    node_b = index * 10 + 2
    return (
        {
            "node_id": node_a,
            "coherence": 4.0,
            "basin_id": parent,
            "is_sink": True,
            "payload": {
                "successor_node_id": node_a,
                "hierarchy_parent": parent,
                "source_construct_id": parent,
            },
        },
        {
            "node_id": node_b,
            "coherence": 2.0,
            "basin_id": parent,
            "payload": {
                "successor_node_id": node_b,
                "hierarchy_parent": parent,
                "source_construct_id": parent,
            },
        },
    )


def _dense_fission_child_nodes(index: int) -> tuple[dict[str, object], ...]:
    parent = f"dense_parent_{index:04d}"
    node_a = index * 10 + 1
    node_b = index * 10 + 2
    return (
        {
            "node_id": node_a,
            "coherence": 2.0,
            "basin_id": f"dense_child_{index:04d}_a",
            "is_sink": True,
            "payload": {
                "hierarchy_parent": parent,
                "source_construct_id": parent,
            },
        },
        {
            "node_id": node_b,
            "coherence": 2.0,
            "basin_id": f"dense_child_{index:04d}_b",
            "is_sink": True,
            "payload": {
                "hierarchy_parent": parent,
                "source_construct_id": parent,
            },
        },
    )


def _dense_fission_edge(index: int) -> dict[str, object]:
    return {
        "edge_id": index * 10 + 3,
        "source_node_id": index * 10 + 1,
        "target_node_id": index * 10 + 2,
        "signed_flux": 1.0,
    }


def _identity(seed_name: str, family: str, steps: int) -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id=f"{family}_{seed_name}",
        model_family=family,
        params_identity="motion_seed_examples",
        seed_name=seed_name,
        seed_source_reference="motion_seed_examples_iter10_authored_projection",
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
        checkpoint_reason="motion_seed_examples_iter10",
        graph_kind="weighted_graph",
        node_count=len(nodes),
        edge_count=len(edges),
        node_records=nodes,
        edge_records=edges,
        family_extensions={
            family: {
                "contract_version": MOTION_SEED_EXAMPLES_SESSION_VERSION,
                "evidence_source": "authored_seed_projection",
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
                "contract_version": MOTION_SEED_EXAMPLES_SESSION_VERSION,
                "event_domain": kind,
                "lifecycle_stage": "completed",
                "topology_mutation": True,
                "primary_node_id": payload_dict.get("node_id"),
            }
        },
    )


def _target_motion_modes(seed: LandscapeSeed) -> tuple[str, ...]:
    extension = seed.extensions.get("motion_seed", {})
    if not isinstance(extension, Mapping):
        return ()
    return tuple(str(item) for item in extension.get("target_motion_modes", ()))


def _select_seed_specs(
    specs: Sequence[MotionAuthoredSeedSpec],
    seed_names: Sequence[str] | None,
) -> tuple[MotionAuthoredSeedSpec, ...]:
    if seed_names is None:
        return tuple(specs)
    wanted = set(seed_names)
    selected = tuple(spec for spec in specs if spec.seed_name in wanted)
    missing = wanted - {spec.seed_name for spec in selected}
    if missing:
        raise ValueError(f"unknown motion authored seed name(s): {sorted(missing)}")
    return selected


def _combined_counts(items: Sequence[Mapping[str, int]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        for key, value in item.items():
            counts[key] = counts.get(key, 0) + int(value)
    return dict(sorted(counts.items()))


def _combined_relationships(
    items: Sequence[Mapping[str, Sequence[str]]],
) -> dict[str, list[str]]:
    relationships: dict[str, list[str]] = {}
    for item in items:
        for key, value in item.items():
            relationships.setdefault(key, []).extend(str(inner) for inner in value)
    return {key: value for key, value in sorted(relationships.items())}


def _seed_motion_summary(session: MotionSeedExamplesSession) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "session_version": session.session_version,
            "session_id": session.session_id,
            "landscape_manifest_path": str(session.session_root / "session_manifest.json"),
            "selected_landscape_example_count": sum(
                len(run.projected_runs) for run in session.runs
            ),
            "runs": [
                {
                    "key": projected.spec.example_name,
                    "runtime_family": projected.spec.runtime_family,
                    "checkpoint_count_loaded": len(projected.spec.checkpoints),
                    "primitive_counts_by_type": _primitive_counts(run.spec.seed),
                    "landscape_relationship_counts": {},
                    "motion_record_counts": dict(projected.observer_record_counts),
                    "motion_relationship_counts": {
                        observer: _relationship_counts(relationships)
                        for observer, relationships in projected.observer_relationships.items()
                    },
                    "visual_notes": [],
                    "motion_report_dir": str(projected.run_dir.parent / "motion_reports"),
                    "source_seed_name": run.spec.seed_name,
                    "source_status": run.spec.source_status,
                }
                for run in session.runs
                for projected in run.projected_runs
            ],
        }
    )


def _primitive_counts(seed: LandscapeSeed) -> dict[str, int]:
    counts: dict[str, int] = {}
    for primitive in seed.primitives:
        counts[primitive.type] = counts.get(primitive.type, 0) + 1
    return dict(sorted(counts.items()))


def _relationship_counts(relationships: Sequence[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for relationship in relationships:
        counts[str(relationship)] = counts.get(str(relationship), 0) + 1
    return dict(sorted(counts.items()))


def _validate_no_runtime_motion_smuggling(value: Any, *, context: str) -> None:
    if isinstance(value, Mapping):
        for key, inner in value.items():
            if str(key) in _FORBIDDEN_SOURCE_KEYS:
                raise ValueError(f"{context}.{key} embeds runtime motion evidence")
            _validate_no_runtime_motion_smuggling(inner, context=f"{context}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, str | bytes):
        for index, inner in enumerate(value):
            _validate_no_runtime_motion_smuggling(inner, context=f"{context}[{index}]")


def _session_manifest(session: MotionSeedExamplesSession) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "session_version": session.session_version,
            "session_id": session.session_id,
            "session_root": str(session.session_root),
            "source_seed_count": len(session.runs),
            "seeds": [
                {
                    "seed_name": run.spec.seed_name,
                    "runtime_family": run.spec.runtime_family,
                    "source_status": run.spec.source_status,
                    "library_seed_path": str(run.library_seed_path),
                    "seed_path": str(run.seed_path),
                    "projected_example_names": [
                        projected.spec.example_name for projected in run.projected_runs
                    ],
                    "run_dirs": [str(projected.run_dir) for projected in run.projected_runs],
                }
                for run in session.runs
            ],
        }
    )


def _readme(session: MotionSeedExamplesSession) -> str:
    if session.session_version == MOTION_LONG_COMPOSITES_SESSION_VERSION:
        description = "Iteration 11 long-window composite runtime projections."
    elif session.session_version == MOTION_DENSE_FISSION_SESSION_VERSION:
        description = "Iteration 12.5 dense confirmed-fission seed projection."
    else:
        description = "Iteration 10 authored seeds and composite runtime projections."
    lines = [
        f"# Motion Authored Seed Examples {session.session_id}",
        "",
        description,
        "",
        "Source seeds declare motion preconditions only. Motion relationships",
        "are inferred from projected runtime telemetry by the motion observers.",
        "",
        f"Reusable authored seeds are also written to `{DEFAULT_MOTION_SEED_LIBRARY_DIR}`.",
        "",
        "## Seeds",
        "",
    ]
    for run in session.runs:
        lines.append(
            f"- `{run.spec.seed_name}` ({run.spec.runtime_family}, {run.spec.source_status})"
        )
    long_flag = (
        " --long-composites"
        if session.session_version == MOTION_LONG_COMPOSITES_SESSION_VERSION
        else ""
    )
    dense_flag = (
        " --dense-fission"
        if session.session_version == MOTION_DENSE_FISSION_SESSION_VERSION
        else ""
    )
    lines.extend(["", "## Rerun", "", "```bash", f"PYTHONPATH=src python -m pygrc.landscapes.motion_seed_examples --output-root {session.session_root.parent.parent} --session-id {session.session_id}{long_flag}{dense_flag}", "```", ""])
    return "\n".join(lines)


def _rerun_script(
    root: Path,
    session_id: str,
    seed_names: Sequence[str] | None,
    *,
    long_composites: bool = False,
    dense_fission: bool = False,
) -> str:
    command = (
        f"PYTHONPATH=src python -m pygrc.landscapes.motion_seed_examples "
        f"--output-root {root} --session-id {session_id}"
    )
    if long_composites:
        command += " --long-composites"
    if dense_fission:
        command += " --dense-fission"
    if seed_names:
        command += "".join(f" --seed {name}" for name in seed_names)
    return "\n".join(["#!/usr/bin/env bash", "set -euo pipefail", command, ""])


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json_dumps(payload), encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", default=str(DEFAULT_MOTION_SEED_OUTPUT_ROOT))
    parser.add_argument("--session-id", default=DEFAULT_MOTION_SEED_SESSION_ID)
    parser.add_argument("--seed", action="append", default=None)
    parser.add_argument(
        "--long-composites",
        action="store_true",
        help="Run Iteration 11 long-window composite seeds instead of Iteration 10 defaults.",
    )
    parser.add_argument(
        "--dense-fission",
        action="store_true",
        help="Run Iteration 12.5 dense confirmed-fission seed instead of Iteration 10 defaults.",
    )
    parser.add_argument(
        "--seed-library-dir",
        default=str(DEFAULT_MOTION_SEED_LIBRARY_DIR),
        help="Reusable authored seed library directory.",
    )
    parser.add_argument("--no-visuals", action="store_true")
    args = parser.parse_args(argv)
    if args.long_composites and args.dense_fission:
        raise SystemExit("--long-composites and --dense-fission are mutually exclusive")
    if args.dense_fission:
        runner = run_motion_dense_fission_examples
    elif args.long_composites:
        runner = run_motion_long_composite_examples
    else:
        runner = run_motion_authored_seed_examples
    session = runner(
        output_root=args.output_root,
        session_id=args.session_id,
        seed_names=args.seed,
        render_visuals=not args.no_visuals,
        seed_library_dir=args.seed_library_dir,
    )
    print(canonical_json_dumps(session.to_mapping()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_MOTION_LONG_COMPOSITE_SESSION_ID",
    "DEFAULT_MOTION_DENSE_FISSION_SESSION_ID",
    "DEFAULT_MOTION_SEED_OUTPUT_ROOT",
    "DEFAULT_MOTION_SEED_SESSION_ID",
    "DEFAULT_MOTION_SEED_LIBRARY_DIR",
    "MOTION_DENSE_FISSION_SESSION_VERSION",
    "MOTION_LONG_COMPOSITES_SESSION_VERSION",
    "MOTION_SEED_EXAMPLES_SESSION_VERSION",
    "MOTION_SEED_EXTENSION_VERSION",
    "MotionAuthoredSeedRun",
    "MotionAuthoredSeedSpec",
    "MotionSeedExamplesSession",
    "default_motion_authored_seed_specs",
    "default_motion_dense_fission_seed_specs",
    "default_motion_long_composite_seed_specs",
    "run_motion_authored_seed_examples",
    "run_motion_dense_fission_examples",
    "run_motion_long_composite_examples",
]
