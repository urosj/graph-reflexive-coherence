"""Post-processing helpers for telemetry-backed experiment reports."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from .io import (
    COMPARISON_REPORT_FILENAME,
    EVENT_ROWS_FILENAME,
    EXPERIMENT_REPORT_FILENAME,
    RUN_SUMMARY_FILENAME,
    STEP_ROWS_FILENAME,
    TELEMETRY_DIRNAME,
    TelemetryArtifactLayout,
)
from .schema import (
    RunTelemetrySummary,
    StepTelemetryRow,
    TelemetryExperimentReport,
)


def build_artifact_references(layout: TelemetryArtifactLayout | None) -> dict[str, Any]:
    """Build repo-shareable artifact references without leaking absolute roots."""

    if layout is None:
        return {}
    run_prefix = _shareable_run_prefix(layout)
    telemetry_prefix = run_prefix / TELEMETRY_DIRNAME
    return {
        "run_id": layout.run_id,
        "run_dir": _path_reference(run_prefix),
        "telemetry_dir": _path_reference(telemetry_prefix),
        "step_rows": _path_reference(telemetry_prefix / STEP_ROWS_FILENAME),
        "event_rows": _path_reference(telemetry_prefix / EVENT_ROWS_FILENAME),
        "run_summary": _path_reference(telemetry_prefix / RUN_SUMMARY_FILENAME),
        "comparison_report": _path_reference(telemetry_prefix / COMPARISON_REPORT_FILENAME),
        "experiment_report": _path_reference(telemetry_prefix / EXPERIMENT_REPORT_FILENAME),
    }


def summarize_numeric_observable_trajectory(
    step_rows: list[StepTelemetryRow] | tuple[StepTelemetryRow, ...],
    *,
    initial_observables: dict[str, Any] | Any,
    final_observables: dict[str, Any] | Any,
) -> dict[str, dict[str, float]]:
    """Summarize numeric observable evolution across one run trajectory."""

    values_by_name: dict[str, list[float]] = {}
    names = set(initial_observables) | set(final_observables)
    for row in step_rows:
        names.update(row.observables.keys())

    for name in sorted(names):
        values: list[float] = []
        for candidate in [initial_observables.get(name)]:
            if _is_finite_number(candidate):
                values.append(float(candidate))
        for row in step_rows:
            candidate = row.observables.get(name)
            if _is_finite_number(candidate):
                values.append(float(candidate))
        for candidate in [final_observables.get(name)]:
            if _is_finite_number(candidate):
                values.append(float(candidate))
        if values:
            values_by_name[name] = values

    return {
        name: {
            "initial": values[0],
            "final": values[-1],
            "minimum": min(values),
            "maximum": max(values),
            "delta": values[-1] - values[0],
        }
        for name, values in sorted(values_by_name.items())
    }


def list_changed_observables(
    *,
    initial_observables: dict[str, Any] | Any,
    final_observables: dict[str, Any] | Any,
) -> tuple[str, ...]:
    """List observable names whose initial and final values differ."""

    changed: list[str] = []
    for name in sorted(set(initial_observables) | set(final_observables)):
        if initial_observables.get(name) != final_observables.get(name):
            changed.append(name)
    return tuple(changed)


def build_run_experiment_report(
    run_summary: RunTelemetrySummary,
    *,
    step_rows: list[StepTelemetryRow] | tuple[StepTelemetryRow, ...],
    artifact_layout: TelemetryArtifactLayout | None = None,
) -> TelemetryExperimentReport:
    """Build the first experiment-facing report payload for one run."""

    return TelemetryExperimentReport(
        family=run_summary.identity.model_family,
        common={
            "report_type": "trajectory_summary_v1",
            "run_id": run_summary.identity.run_id,
            "model_family": run_summary.identity.model_family,
            "params_identity": run_summary.identity.params_identity,
            "resolved_params": run_summary.resolved_params,
            "raw_params": run_summary.raw_params,
            "parameter_overrides": run_summary.parameter_overrides,
            "seed_name": run_summary.identity.seed_name,
            "seed_source_reference": run_summary.identity.seed_source_reference,
            "seed_path": run_summary.identity.seed_path,
            "param_family": run_summary.identity.param_family,
            "rng_seed": run_summary.identity.rng_seed,
            "requested_steps": run_summary.identity.requested_steps,
            "source_artifacts": build_artifact_references(artifact_layout),
            "completed_steps": run_summary.completed_steps,
            "final_step_index": run_summary.final_step_index,
            "initial_time": run_summary.initial_time,
            "final_time": run_summary.final_time,
            "total_event_count": run_summary.total_event_count,
            "event_counts_by_kind": run_summary.event_counts_by_kind,
            "changed_observables": list(
                list_changed_observables(
                    initial_observables=run_summary.initial_observables,
                    final_observables=run_summary.final_observables,
                )
            ),
            "numeric_observable_trajectory": summarize_numeric_observable_trajectory(
                step_rows,
                initial_observables=run_summary.initial_observables,
                final_observables=run_summary.final_observables,
            ),
            "checkpoint_overview": {
                "step_count": len(step_rows),
                "first_step_index": None if not step_rows else step_rows[0].step_index,
                "last_step_index": None if not step_rows else step_rows[-1].step_index,
            },
        },
        extensions=run_summary.family_extensions,
    )


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value)


def _shareable_run_prefix(layout: TelemetryArtifactLayout) -> Any:
    run_dir = Path(layout.run_id)
    if layout.root_dir.is_absolute():
        return run_dir
    return layout.run_dir


def _path_reference(path: Any) -> str:
    return Path(path).as_posix()


__all__ = [
    "build_artifact_references",
    "build_run_experiment_report",
    "list_changed_observables",
    "summarize_numeric_observable_trajectory",
]
