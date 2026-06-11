"""Private result dataclasses for telemetry experiment helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pygrc.core import StepResult
from pygrc.models import (
    GRC9,
    GRC9LandscapeRunResult,
    GRCV2LandscapeRunResult,
    GRCV3,
    GRCV3LandscapeRunResult,
)

from .recorder import TelemetryCaptureResult
from .schema import TelemetryComparisonReport, TelemetryExperimentReport


@dataclass(frozen=True)
class GRCV2RepresentativeExperimentResult:
    """Representative `GRCV2` experiment bundle for the first telemetry lane."""

    family_name: str
    num_steps: int
    rng_seed: int | None
    cell1_seed_path: Path
    cell4_seed_path: Path
    cell1_run: GRCV2LandscapeRunResult
    cell4_run: GRCV2LandscapeRunResult
    cell1_report: TelemetryExperimentReport
    cell4_report: TelemetryExperimentReport
    comparison_report: TelemetryComparisonReport


@dataclass
class GRCV3RepresentativeRunResult:
    """One telemetry-backed representative GRCV3 runtime lane."""

    role: str
    seed_name: str
    model: GRCV3
    initial_observables: dict[str, Any]
    step_results: list[StepResult]
    final_observables: dict[str, Any]
    telemetry: TelemetryCaptureResult
    final_snapshot_digest: str


@dataclass(frozen=True)
class GRCV3RepresentativeExperimentResult:
    """Representative telemetry-backed GRCV3 experiment bundle."""

    lane_name: str
    num_steps: int
    primary_run: GRCV3RepresentativeRunResult
    replay_run: GRCV3RepresentativeRunResult
    primary_report: TelemetryExperimentReport
    replay_report: TelemetryExperimentReport
    comparison_report: TelemetryComparisonReport


@dataclass
class GRC9RepresentativeRunResult:
    """One telemetry-backed representative GRC9 runtime lane."""

    role: str
    seed_name: str
    model: GRC9
    initial_observables: dict[str, Any]
    step_results: list[StepResult]
    final_observables: dict[str, Any]
    telemetry: TelemetryCaptureResult
    final_snapshot_digest: str


@dataclass(frozen=True)
class GRC9RepresentativeExperimentResult:
    """Representative telemetry-backed GRC9 experiment bundle."""

    lane_name: str
    num_steps: int
    primary_run: GRC9RepresentativeRunResult
    replay_run: GRC9RepresentativeRunResult
    primary_report: TelemetryExperimentReport
    replay_report: TelemetryExperimentReport
    comparison_report: TelemetryComparisonReport


@dataclass(frozen=True)
class GRC9LandscapeExperimentResult:
    """Canonical telemetry-backed GRC9 landscape experiment bundle."""

    profile_name: str
    num_steps: int
    cell1_seed_path: Path
    cell4_seed_path: Path
    cell1_run: GRC9LandscapeRunResult
    cell4_run: GRC9LandscapeRunResult
    cell1_report: TelemetryExperimentReport
    cell4_report: TelemetryExperimentReport
    comparison_report: TelemetryComparisonReport


@dataclass(frozen=True)
class GRCV3LandscapeExperimentResult:
    """Canonical telemetry-backed GRCV3 landscape experiment bundle."""

    profile_name: str
    num_steps: int
    cell1_seed_path: Path
    cell4_seed_path: Path
    cell1_run: GRCV3LandscapeRunResult
    cell4_run: GRCV3LandscapeRunResult
    cell1_report: TelemetryExperimentReport
    cell4_report: TelemetryExperimentReport
    comparison_report: TelemetryComparisonReport


__all__ = [
    "GRC9LandscapeExperimentResult",
    "GRC9RepresentativeExperimentResult",
    "GRC9RepresentativeRunResult",
    "GRCV2RepresentativeExperimentResult",
    "GRCV3RepresentativeRunResult",
    "GRCV3RepresentativeExperimentResult",
    "GRCV3LandscapeExperimentResult",
]
