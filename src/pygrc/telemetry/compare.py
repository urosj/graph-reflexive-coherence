"""Comparison helpers for telemetry-backed experiment reasoning."""

from __future__ import annotations

import math
from typing import Any

from .io import TelemetryArtifactLayout
from .reports import build_artifact_references
from .schema import RunTelemetrySummary, TelemetryComparisonReport


def compare_run_summaries(
    left: RunTelemetrySummary,
    right: RunTelemetrySummary,
    *,
    left_artifact_layout: TelemetryArtifactLayout | None = None,
    right_artifact_layout: TelemetryArtifactLayout | None = None,
) -> TelemetryComparisonReport:
    """Build a pairwise comparison report from two run summaries."""

    return TelemetryComparisonReport(
        family=right.identity.model_family,
        common={
            "report_type": "run_summary_comparison_v1",
            "left_run_id": left.identity.run_id,
            "right_run_id": right.identity.run_id,
            "left_model_family": left.identity.model_family,
            "right_model_family": right.identity.model_family,
            "left_params_identity": left.identity.params_identity,
            "right_params_identity": right.identity.params_identity,
            "left_resolved_params": left.resolved_params,
            "right_resolved_params": right.resolved_params,
            "left_raw_params": left.raw_params,
            "right_raw_params": right.raw_params,
            "left_parameter_overrides": left.parameter_overrides,
            "right_parameter_overrides": right.parameter_overrides,
            "left_param_family": left.identity.param_family,
            "right_param_family": right.identity.param_family,
            "left_source_artifacts": build_artifact_references(left_artifact_layout),
            "right_source_artifacts": build_artifact_references(right_artifact_layout),
            "completed_steps_right_minus_left": right.completed_steps - left.completed_steps,
            "total_event_count_right_minus_left": (
                right.total_event_count - left.total_event_count
            ),
            "event_counts_by_kind_right_minus_left": _diff_int_mappings(
                dict(left.event_counts_by_kind),
                dict(right.event_counts_by_kind),
            ),
            "final_observables_right_minus_left": _diff_numeric_observables(
                dict(left.final_observables),
                dict(right.final_observables),
            ),
        },
        extensions={
            "left": dict(left.family_extensions),
            "right": dict(right.family_extensions),
        },
    )


def _diff_int_mappings(left: dict[str, Any], right: dict[str, Any]) -> dict[str, int]:
    return {
        key: int(right.get(key, 0)) - int(left.get(key, 0))
        for key in sorted(set(left) | set(right))
    }


def _diff_numeric_observables(left: dict[str, Any], right: dict[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    for key in sorted(set(left) | set(right)):
        left_value = left.get(key)
        right_value = right.get(key)
        if _is_finite_number(left_value) and _is_finite_number(right_value):
            result[key] = float(right_value) - float(left_value)
    return result


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value)


__all__ = ["compare_run_summaries"]
