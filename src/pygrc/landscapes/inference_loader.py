"""Family-agnostic artifact loader for landscape inference."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pygrc.core import InvalidLandscapeSeedError, canonicalize_json_value

from .inference import (
    LANDSCAPE_INFERENCE_RUNTIME_FAMILIES,
    LandscapeInferenceTopLevelExtension,
    LandscapeInferenceWindow,
    landscape_inference_top_level_mapping,
)
from .seed import (
    LandscapeSeed,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
)


if TYPE_CHECKING:
    from pygrc.telemetry.io import TelemetryArtifactLayout, TelemetryArtifactPack


INFERRED_OBSERVED_LANDSCAPE_SOURCE_KIND = "inferred_observed_landscape"
TELEMETRY_DIRNAME = "telemetry"
STEP_ROWS_FILENAME = "steps.jsonl"
EVENT_ROWS_FILENAME = "events.jsonl"
RUN_SUMMARY_FILENAME = "run_summary.json"

_RUNTIME_FAMILY_PRIORITY: tuple[str, ...] = ("grc9v3", "grc9", "grcv3")


@dataclass(frozen=True)
class LandscapeInferenceArtifactAvailability:
    """Availability summary for artifacts consumed by the Iteration 2 loader."""

    step_rows_available: bool
    event_rows_available: bool
    run_summary_available: bool
    graph_checkpoint_index_available: bool
    graph_checkpoint_count: int
    missing_artifacts: tuple[str, ...] = ()

    def to_mapping(self) -> dict[str, Any]:
        return {
            "step_rows_available": self.step_rows_available,
            "event_rows_available": self.event_rows_available,
            "run_summary_available": self.run_summary_available,
            "graph_checkpoint_index_available": self.graph_checkpoint_index_available,
            "graph_checkpoint_count": int(self.graph_checkpoint_count),
            "missing_artifacts": list(self.missing_artifacts),
        }


@dataclass(frozen=True)
class LandscapeInferenceArtifactLoadResult:
    """Loaded artifact pack plus the minimal observed landscape seed."""

    artifact_root: Path
    telemetry_layout: TelemetryArtifactLayout
    telemetry_pack: TelemetryArtifactPack
    source_runtime_family: str
    inference_window: LandscapeInferenceWindow
    availability: LandscapeInferenceArtifactAvailability
    inferred_seed: LandscapeSeed

    def to_summary_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "artifact_root": str(self.artifact_root),
                "run_id": self.telemetry_pack.run_summary.identity.run_id,
                "source_runtime_family": self.source_runtime_family,
                "inference_window": self.inference_window.to_mapping(),
                "availability": self.availability.to_mapping(),
                "inferred_seed_primitive_count": len(self.inferred_seed.primitives),
            }
        )


def resolve_landscape_inference_artifact_layout(path: str | Path) -> TelemetryArtifactLayout:
    """Resolve a run directory or telemetry directory to a telemetry layout."""

    from pygrc.telemetry.io import TelemetryArtifactError, TelemetryArtifactLayout

    artifact_path = Path(path)
    telemetry_dir = artifact_path if artifact_path.name == TELEMETRY_DIRNAME else artifact_path / TELEMETRY_DIRNAME
    if telemetry_dir.name != TELEMETRY_DIRNAME:
        raise TelemetryArtifactError("artifact path must be a run directory or telemetry directory")
    run_dir = telemetry_dir.parent
    root_dir = run_dir.parent
    return TelemetryArtifactLayout(
        root_dir=root_dir,
        run_id=run_dir.name,
        run_dir=run_dir,
        telemetry_dir=telemetry_dir,
        step_rows_path=telemetry_dir / STEP_ROWS_FILENAME,
        event_rows_path=telemetry_dir / EVENT_ROWS_FILENAME,
        run_summary_path=telemetry_dir / RUN_SUMMARY_FILENAME,
        comparison_report_path=telemetry_dir / "comparison_report.json",
        experiment_report_path=telemetry_dir / "experiment_report.json",
        graph_checkpoints_dir=telemetry_dir / "graph_checkpoints",
        graph_checkpoint_index_path=telemetry_dir / "graph_checkpoints" / "index.json",
    )


def inspect_landscape_inference_artifact_availability(
    layout: TelemetryArtifactLayout,
    *,
    graph_checkpoint_count: int = 0,
) -> LandscapeInferenceArtifactAvailability:
    """Return deterministic availability status for one telemetry layout."""

    missing: list[str] = []
    if not layout.step_rows_path.exists():
        missing.append(str(layout.step_rows_path))
    if not layout.event_rows_path.exists():
        missing.append(str(layout.event_rows_path))
    if not layout.run_summary_path.exists():
        missing.append(str(layout.run_summary_path))
    return LandscapeInferenceArtifactAvailability(
        step_rows_available=layout.step_rows_path.exists(),
        event_rows_available=layout.event_rows_path.exists(),
        run_summary_available=layout.run_summary_path.exists(),
        graph_checkpoint_index_available=layout.graph_checkpoint_index_path.exists(),
        graph_checkpoint_count=graph_checkpoint_count,
        missing_artifacts=tuple(missing),
    )


def detect_landscape_inference_runtime_family(pack: TelemetryArtifactPack) -> str:
    """Detect the runtime family from shared telemetry family extensions."""

    extension_keys: set[str] = set()
    extension_keys.update(pack.run_summary.family_extensions.keys())
    for row in pack.step_rows:
        extension_keys.update(row.family_extensions.keys())
    for row in pack.event_rows:
        extension_keys.update(row.family_extensions.keys())
    if pack.graph_checkpoint_index is not None:
        extension_keys.update(pack.graph_checkpoint_index.family_extensions.keys())
    for checkpoint in pack.graph_checkpoints:
        extension_keys.update(checkpoint.family_extensions.keys())

    for family in _RUNTIME_FAMILY_PRIORITY:
        if family in extension_keys:
            return family

    model_family = pack.run_summary.identity.model_family.lower().replace("-", "")
    for family in LANDSCAPE_INFERENCE_RUNTIME_FAMILIES:
        if model_family == family:
            return family
    raise InvalidLandscapeSeedError("could not detect supported landscape inference runtime family")


def select_landscape_inference_window(
    pack: TelemetryArtifactPack,
    *,
    policy: str = "whole_run",
    start_step: int | None = None,
    end_step: int | None = None,
    final_step_count: int | None = None,
    event_step: int | None = None,
    radius: int | None = None,
) -> LandscapeInferenceWindow:
    """Select a deterministic step window for the loaded artifacts."""

    min_step, max_step = _artifact_step_bounds(pack)
    if policy == "explicit":
        if start_step is None or end_step is None:
            raise InvalidLandscapeSeedError("explicit inference windows require start_step and end_step")
        window = LandscapeInferenceWindow(start_step=start_step, end_step=end_step, policy=policy)
    elif policy == "final":
        count = 1 if final_step_count is None else final_step_count
        if count <= 0:
            raise InvalidLandscapeSeedError("final_step_count must be > 0")
        window = LandscapeInferenceWindow(
            start_step=max(min_step, max_step - count + 1),
            end_step=max_step,
            policy=policy,
        )
    elif policy == "event_centered":
        if event_step is None:
            raise InvalidLandscapeSeedError("event_centered inference windows require event_step")
        resolved_radius = 1 if radius is None else radius
        if resolved_radius < 0:
            raise InvalidLandscapeSeedError("event-centered radius must be >= 0")
        window = LandscapeInferenceWindow(
            start_step=max(min_step, event_step - resolved_radius),
            end_step=min(max_step, event_step + resolved_radius),
            policy=policy,
        )
    elif policy == "whole_run":
        window = LandscapeInferenceWindow(start_step=min_step, end_step=max_step, policy=policy)
    else:
        raise InvalidLandscapeSeedError(
            "inference window policy must be explicit, final, event_centered, or whole_run"
        )
    if window.start_step < min_step or window.end_step > max_step:
        raise InvalidLandscapeSeedError("inference window falls outside loaded artifact step range")
    return window


def load_landscape_inference_artifacts(
    path: str | Path,
    *,
    window_policy: str = "whole_run",
    start_step: int | None = None,
    end_step: int | None = None,
    final_step_count: int | None = None,
    event_step: int | None = None,
    radius: int | None = None,
) -> LandscapeInferenceArtifactLoadResult:
    """Load one run/lane and build an empty observed `LandscapeSeed` shell."""

    from pygrc.telemetry.io import load_telemetry_artifact_pack

    layout = resolve_landscape_inference_artifact_layout(path)
    pack = load_telemetry_artifact_pack(layout)
    runtime_family = detect_landscape_inference_runtime_family(pack)
    inference_window = select_landscape_inference_window(
        pack,
        policy=window_policy,
        start_step=start_step,
        end_step=end_step,
        final_step_count=final_step_count,
        event_step=event_step,
        radius=radius,
    )
    availability = inspect_landscape_inference_artifact_availability(
        layout,
        graph_checkpoint_count=len(pack.graph_checkpoints),
    )
    inferred_seed = build_minimal_landscape_inference_seed(
        pack,
        artifact_root=layout.run_dir,
        source_runtime_family=runtime_family,
        inference_window=inference_window,
    )
    return LandscapeInferenceArtifactLoadResult(
        artifact_root=layout.run_dir,
        telemetry_layout=layout,
        telemetry_pack=pack,
        source_runtime_family=runtime_family,
        inference_window=inference_window,
        availability=availability,
        inferred_seed=inferred_seed,
    )


def build_minimal_landscape_inference_seed(
    pack: TelemetryArtifactPack,
    *,
    artifact_root: str | Path,
    source_runtime_family: str,
    inference_window: LandscapeInferenceWindow,
) -> LandscapeSeed:
    """Build the Iteration 2 empty observed landscape seed shell."""

    identity = pack.run_summary.identity
    extension = LandscapeInferenceTopLevelExtension(
        source_session_id=_source_session_id_from_path(artifact_root),
        source_artifact_paths=(str(artifact_root),),
        source_runtime_family=source_runtime_family,
        inference_window=inference_window,
    )
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(
            name=f"observed_{source_runtime_family}_{identity.run_id}",
            source_kind=INFERRED_OBSERVED_LANDSCAPE_SOURCE_KIND,
            source_reference=str(artifact_root),
            source_schema_version="landscape_inference_iter1_v1",
            source_domain="runtime_observation",
            description="Empty observed landscape shell; classifiers have not emitted primitives yet.",
            tags=["landscape_inference", source_runtime_family],
            translator_name="pygrc.landscape_inference_loader",
            translator_version="iter2_v1",
            translation_mode="observed_artifact_load",
        ),
        constitutive_profile=_minimal_constitutive_profile(pack.run_summary.resolved_params),
        primitives=[],
        transport_intent=[],
        extensions={
            "landscape_inference": landscape_inference_top_level_mapping(extension),
            "landscape_inference_loader": {
                "loader_version": "landscape_inference_iter2_v1",
                "source_runtime_family": source_runtime_family,
                "run_id": identity.run_id,
                "artifact_root": str(artifact_root),
            },
        },
    )


def _artifact_step_bounds(pack: TelemetryArtifactPack) -> tuple[int, int]:
    step_indices = [row.step_index for row in pack.step_rows]
    if not step_indices:
        return (pack.run_summary.final_step_index, pack.run_summary.final_step_index)
    return (min(step_indices), max(step_indices))


def _source_session_id_from_path(path: str | Path) -> str:
    for part in reversed(Path(path).parts):
        if part.startswith("S") and part[1:].isdigit():
            return part
    return Path(path).name


def _minimal_constitutive_profile(resolved_params: Mapping[str, Any]) -> SeedConstitutiveProfile:
    evolution = resolved_params.get("evolution", {})
    if not isinstance(evolution, Mapping):
        evolution = {}
    dt = evolution.get("dt", resolved_params.get("dt", 1.0))
    try:
        resolved_dt = float(dt)
    except (TypeError, ValueError):
        resolved_dt = 1.0
    if resolved_dt <= 0.0:
        resolved_dt = 1.0
    return SeedConstitutiveProfile(
        lambda_c=1.0,
        xi_c=1.0,
        zeta_c=0.0,
        kappa_c=0.0,
        dt=resolved_dt,
        potential=SeedPotential(type="observed_runtime_artifact", params={}),
        notes="Placeholder profile for an inferred observed landscape shell.",
    )


__all__ = [
    "INFERRED_OBSERVED_LANDSCAPE_SOURCE_KIND",
    "LandscapeInferenceArtifactAvailability",
    "LandscapeInferenceArtifactLoadResult",
    "build_minimal_landscape_inference_seed",
    "detect_landscape_inference_runtime_family",
    "inspect_landscape_inference_artifact_availability",
    "load_landscape_inference_artifacts",
    "resolve_landscape_inference_artifact_layout",
    "select_landscape_inference_window",
]
