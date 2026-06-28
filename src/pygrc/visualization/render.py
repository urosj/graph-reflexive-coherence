"""Artifact-driven rendering helpers for first-pass visualization outputs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/pygrc-matplotlib")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from pygrc.telemetry import (
    EventTelemetryRow,
    RunTelemetrySummary,
    StepTelemetryRow,
    TelemetryArtifactPack,
    TelemetryComparisonReport,
    TelemetryExperimentReport,
)

from .layout import ComparisonVisualizationLayout, RunVisualizationLayout


DEFAULT_RUN_OBSERVABLES: tuple[str, ...] = (
    "budget_current",
    "budget_error",
    "num_nodes",
    "num_edges",
    "sink_count",
    "birth_count",
    "average_conductance",
    "abundance",
    "weighted_abundance",
)

DEFAULT_COMPARISON_OBSERVABLES: tuple[str, ...] = (
    "budget_current",
    "num_nodes",
    "num_edges",
    "sink_count",
    "birth_count",
    "average_conductance",
)

DEFAULT_GRCV3_RUN_OBSERVABLES: tuple[str, ...] = (
    "active_basin_count",
    "max_hierarchy_depth",
    "geometric_seed_count",
    "geometric_validated_basin_count",
    "active_split_count",
    "spark_event_count",
    "choice_regime_count",
    "collapse_event_count",
    "family_extensions.grcv3.signed_hessian.hessian_sign",
    "family_extensions.grcv3.spark_state.split_registry_size",
    "family_extensions.grcv3.hierarchy_state.hierarchy_node_count",
    "family_extensions.grcv3.choice_state.evaluated_node_count",
)

DEFAULT_GRCV3_COMPARISON_OBSERVABLES: tuple[str, ...] = (
    "active_basin_count",
    "max_hierarchy_depth",
    "geometric_validated_basin_count",
    "active_split_count",
    "spark_event_count",
    "family_extensions.grcv3.signed_hessian.hessian_sign",
    "family_extensions.grcv3.hierarchy_state.hierarchy_node_count",
)

DEFAULT_GRC9_RUN_OBSERVABLES: tuple[str, ...] = (
    "num_nodes",
    "num_port_edges",
    "spark_count",
    "expansion_count",
    "budget_error",
    "family_extensions.grc9.port_chart.num_nodes",
    "family_extensions.grc9.port_chart.num_port_edges",
    "family_extensions.grc9.port_chart.saturated_node_count",
    "family_extensions.grc9.port_chart.near_saturated_node_count",
    "family_extensions.grc9.row_tensor.row_tensor_mean",
    "family_extensions.grc9.row_tensor.row_tensor_anisotropy_max",
    "family_extensions.grc9.row_tensor.row_mismatch_term_max",
    "family_extensions.grc9.column_diagnostic.column_proxy_candidate_count",
    "family_extensions.grc9.column_diagnostic.sign_crossing_candidate_count",
    "family_extensions.grc9.column_diagnostic.column_profile_sparsity",
    "family_extensions.grc9.transport.conductance_mean",
    "family_extensions.grc9.transport.flux_abs_sum",
    "family_extensions.grc9.identity_abundance.sink_count",
    "family_extensions.grc9.identity_abundance.basin_size_max",
    "family_extensions.grc9.identity_abundance.successor_tie_count",
    "family_extensions.grc9.identity_abundance.scale_weighted_abundance",
    "family_extensions.grc9.coarse_graining.coarse_fields_list.length",
    "family_extensions.grc9.coarse_graining.coarse_field_types.length",
    "family_extensions.grc9.budget_correction.budget_error",
)

DEFAULT_GRC9_COMPARISON_OBSERVABLES: tuple[str, ...] = (
    "num_nodes",
    "num_port_edges",
    "spark_count",
    "expansion_count",
    "family_extensions.grc9.port_chart.num_nodes",
    "family_extensions.grc9.port_chart.num_port_edges",
    "family_extensions.grc9.port_chart.saturated_node_count",
    "family_extensions.grc9.column_diagnostic.column_proxy_candidate_count",
    "family_extensions.grc9.column_diagnostic.sign_crossing_candidate_count",
    "family_extensions.grc9.transport.flux_abs_sum",
    "family_extensions.grc9.identity_abundance.sink_count",
    "family_extensions.grc9.identity_abundance.basin_size_max",
    "family_extensions.grc9.identity_abundance.successor_tie_count",
    "family_extensions.grc9.coarse_graining.coarse_fields_list.length",
)

DEFAULT_GRC9V3_RUN_OBSERVABLES: tuple[str, ...] = (
    "num_nodes",
    "num_port_edges",
    "event_count",
    "budget_error",
    "family_extensions.grc9v3.port_chart.num_nodes",
    "family_extensions.grc9v3.port_chart.num_port_edges",
    "family_extensions.grc9v3.port_chart.saturated_node_count",
    "family_extensions.grc9v3.row_basis_differential.gradient_norm_mean",
    "family_extensions.grc9v3.row_basis_differential.signed_hessian_mean",
    "family_extensions.grc9v3.row_basis_differential.current_min_signed_hessian_min",
    "family_extensions.grc9v3.hybrid_tensor.tensor_trace_mean",
    "family_extensions.grc9v3.hybrid_tensor.tensor_anisotropy_max",
    "family_extensions.grc9v3.transport.flux_abs_sum",
    "family_extensions.grc9v3.identity_basin.sink_count",
    "family_extensions.grc9v3.identity_basin.basin_count",
    "family_extensions.grc9v3.identity_basin.daughter_sink_count",
    "family_extensions.grc9v3.hierarchy_state.max_hierarchy_depth",
    "family_extensions.grc9v3.hybrid_spark_state.hybrid_spark_candidate_count",
    "family_extensions.grc9v3.hybrid_spark_state.completed_hybrid_spark_count",
    "family_extensions.grc9v3.hybrid_spark_state.candidate_pass_rate",
    "family_extensions.grc9v3.hybrid_spark_state.last_candidate_min_abs_column_h",
    "family_extensions.grc9v3.hybrid_spark_state.last_candidate_column_h_branch_hit",
    "family_extensions.grc9v3.choice_collapse.choice_regime_count",
    "family_extensions.grc9v3.choice_collapse.collapse_registry_count",
    "family_extensions.grc9v3.growth_state.growth_event_count",
    "family_extensions.grc9v3.budget_correction.budget_error",
)

DEFAULT_LGRC9V3_RUN_OBSERVABLES: tuple[str, ...] = (
    "scheduler_event_index",
    "checkpoint_index",
    "event_time_key",
    "packet_count",
    "event_queue_length",
    "in_flight_packet_total",
    "conserved_budget_total",
    "arrival_eligibility_count",
    "local_update_count",
    "causal_spark_diagnostic_count",
    "topology_event_count",
    "boundary_birth_trial_queue_length",
    "family_extensions.lgrc9v3.scheduler_event_index",
    "family_extensions.lgrc9v3.checkpoint_index",
    "family_extensions.lgrc9v3.event_time_key",
    "family_extensions.lgrc9v3.packet_ledger.in_flight_packet_total",
    "family_extensions.lgrc9v3.packet_ledger.event_queue_length",
    "family_extensions.lgrc9v3.local_update_count",
    "family_extensions.lgrc9v3.causal_spark_evaluation_index",
    "family_extensions.lgrc9v3.causal_spark_diagnostic_count",
    "family_extensions.lgrc9v3.topology_event_count",
    "family_extensions.lgrc9v3.multi_basin_formation.child_basin_state_record_count",
    "family_extensions.lgrc9v3.multi_basin_formation.clean_replay_record_count",
    "family_extensions.lgrc9v3.multi_basin_formation.failed_closed_control_count",
    "family_extensions.lgrc9v3.multi_basin_formation.failed_open_control_count",
)


def render_run_visual_bundle(
    pack: TelemetryArtifactPack,
    *,
    report: TelemetryExperimentReport | None = None,
    layout: RunVisualizationLayout,
    observables: Sequence[str] = DEFAULT_RUN_OBSERVABLES,
) -> RunVisualizationLayout:
    """Render the first-pass visualization bundle for one telemetry run."""

    active_report = report if report is not None else pack.experiment_report
    _ensure_parent(layout.trajectory_figure_path)
    _render_run_trajectory_figure(pack.run_summary, pack.step_rows, layout.trajectory_figure_path, observables)
    _render_event_timeline(pack.step_rows, layout.event_timeline_path, event_rows=pack.event_rows)
    if active_report is not None:
        _render_run_report_panel(active_report, layout.report_panel_path)
    return layout


def render_comparison_visual_bundle(
    left_pack: TelemetryArtifactPack,
    right_pack: TelemetryArtifactPack,
    *,
    comparison_report: TelemetryComparisonReport | None = None,
    layout: ComparisonVisualizationLayout,
    observables: Sequence[str] = DEFAULT_COMPARISON_OBSERVABLES,
) -> ComparisonVisualizationLayout:
    """Render the first-pass pairwise comparison visualization bundle."""

    active_report = comparison_report
    if active_report is None:
        active_report = left_pack.comparison_report or right_pack.comparison_report
    _ensure_parent(layout.trajectory_figure_path)
    _render_comparison_trajectory_figure(
        left_pack.run_summary,
        left_pack.step_rows,
        right_pack.run_summary,
        right_pack.step_rows,
        layout.trajectory_figure_path,
        observables,
    )
    if active_report is not None:
        _render_comparison_report_panel(active_report, layout.report_panel_path)
    return layout


def _render_run_trajectory_figure(
    run_summary: RunTelemetrySummary,
    step_rows: Sequence[StepTelemetryRow],
    output_path: Path,
    observables: Sequence[str],
) -> None:
    names = [name for name in observables if _has_numeric_trajectory(name, run_summary, step_rows)]
    figure, axes = _create_grid(len(names), ncols=3, figsize=(14, 3.6 * max(1, math.ceil(len(names) / 3))))
    x_label = _trajectory_x_label(run_summary.identity.model_family)
    for axis, name in zip(axes, names, strict=False):
        xs, ys = _trajectory_series(name, run_summary, step_rows)
        axis.plot(xs, ys, color="#1f77b4", linewidth=1.8)
        axis.scatter([xs[0], xs[-1]], [ys[0], ys[-1]], color="#d62728", s=18, zorder=3)
        axis.set_title(_format_series_name(name))
        axis.set_xlabel(x_label)
        axis.grid(True, alpha=0.25)
        if name == "budget_error":
            axis.axhline(0.0, color="#444444", linewidth=1.0, linestyle="--", alpha=0.7)
    _hide_unused_axes(axes[len(names) :])
    figure.suptitle(
        f"{run_summary.identity.seed_name or run_summary.identity.run_id} trajectory",
        fontsize=14,
    )
    figure.tight_layout()
    figure.savefig(output_path, dpi=140)
    plt.close(figure)


def _render_event_timeline(
    step_rows: Sequence[StepTelemetryRow],
    output_path: Path,
    *,
    event_rows: Sequence[EventTelemetryRow] = (),
) -> None:
    figure, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    x_label = _timeline_x_label(step_rows, event_rows)
    steps_with_events = [row.step_index for row in step_rows if row.event_count > 0]
    all_steps = [row.step_index for row in step_rows]
    all_counts = [row.event_count for row in step_rows]

    if steps_with_events:
        categorized_events = _categorized_event_points(event_rows)
        if categorized_events:
            categories = tuple(dict.fromkeys(category for _, category in categorized_events))
            y_by_category = {category: float(index + 1) for index, category in enumerate(categories)}
            for category in categories:
                xs = [
                    step_index
                    for step_index, event_category in categorized_events
                    if event_category == category
                ]
                axes[0].scatter(
                    xs,
                    [y_by_category[category]] * len(xs),
                    color=_event_category_color(category),
                    s=24,
                    label=category,
                )
            axes[0].set_ylim(0.5, len(categories) + 0.5)
            axes[0].set_yticks(
                [y_by_category[category] for category in categories],
                labels=[_format_event_category(category) for category in categories],
            )
            axes[0].legend(loc="upper right", fontsize=7)
        else:
            axes[0].scatter(steps_with_events, [1.0] * len(steps_with_events), color="#d62728", s=18)
            axes[0].set_ylim(0.8, 1.2)
            axes[0].set_yticks([1.0], labels=["events"])
    else:
        axes[0].text(0.5, 0.5, "No events recorded", ha="center", va="center", transform=axes[0].transAxes)
        axes[0].set_yticks([])
    axes[0].set_title("Event timeline")
    axes[0].grid(True, axis="x", alpha=0.25)

    axes[1].bar(all_steps, all_counts, color="#1f77b4", width=0.9)
    axes[1].set_title("Per-step event counts")
    axes[1].set_xlabel(x_label)
    axes[1].set_ylabel("count")
    axes[1].grid(True, axis="y", alpha=0.25)

    figure.tight_layout()
    figure.savefig(output_path, dpi=140)
    plt.close(figure)


def _render_run_report_panel(report: TelemetryExperimentReport, output_path: Path) -> None:
    _render_text_panel(_build_run_report_lines(report), "Run report", output_path)


def _render_comparison_trajectory_figure(
    left_summary: RunTelemetrySummary,
    left_rows: Sequence[StepTelemetryRow],
    right_summary: RunTelemetrySummary,
    right_rows: Sequence[StepTelemetryRow],
    output_path: Path,
    observables: Sequence[str],
) -> None:
    names = [
        name
        for name in observables
        if _has_numeric_trajectory(name, left_summary, left_rows)
        and _has_numeric_trajectory(name, right_summary, right_rows)
    ]
    figure, axes = _create_grid(len(names), ncols=3, figsize=(14, 3.6 * max(1, math.ceil(len(names) / 3))))
    left_label = left_summary.identity.seed_name or left_summary.identity.run_id
    right_label = right_summary.identity.seed_name or right_summary.identity.run_id
    for axis, name in zip(axes, names, strict=False):
        left_xs, left_ys = _trajectory_series(name, left_summary, left_rows)
        right_xs, right_ys = _trajectory_series(name, right_summary, right_rows)
        axis.plot(left_xs, left_ys, color="#1f77b4", linewidth=1.8, label=left_label)
        axis.plot(right_xs, right_ys, color="#d62728", linewidth=1.8, label=right_label)
        axis.set_title(_format_series_name(name))
        axis.set_xlabel("step")
        axis.grid(True, alpha=0.25)
        if name == "budget_error":
            axis.axhline(0.0, color="#444444", linewidth=1.0, linestyle="--", alpha=0.7)
    if axes:
        axes[0].legend(loc="best")
    _hide_unused_axes(axes[len(names) :])
    figure.suptitle(f"{left_label} vs {right_label}", fontsize=14)
    figure.tight_layout()
    figure.savefig(output_path, dpi=140)
    plt.close(figure)


def _render_comparison_report_panel(report: TelemetryComparisonReport, output_path: Path) -> None:
    _render_text_panel(_build_comparison_report_lines(report), "Comparison report", output_path)


def _build_run_report_lines(report: TelemetryExperimentReport) -> list[str]:
    lines = [
        f"run_id: {report.common['run_id']}",
        f"seed_name: {report.common.get('seed_name')}",
        f"param_family: {report.common.get('param_family')}",
        f"completed_steps: {report.common['completed_steps']}",
        f"total_event_count: {report.common['total_event_count']}",
        f"changed_observables: {', '.join(report.common['changed_observables']) or '<none>'}",
        f"params_identity: {report.common.get('params_identity')}",
        f"resolved_dt: {report.common['resolved_params'].get('dt')}",
    ]
    event_counts = report.common.get("event_counts_by_kind", {})
    if event_counts:
        lines.append("event_counts_by_kind:")
        lines.extend(f"  {key}: {value}" for key, value in sorted(event_counts.items()))
    optional_common_keys = (
        "fixture_name",
        "final_snapshot_digest",
        "replay_final_snapshot_digest",
        "replay_step_rows_match",
        "replay_event_rows_match",
        "replay_digest_match",
        "checkpoint_count",
    )
    for key in optional_common_keys:
        if key in report.common:
            lines.append(f"{key}: {report.common[key]}")
    lines.append("checkpoint_overview:")
    for key, value in report.common["checkpoint_overview"].items():
        lines.append(f"  {key}: {value}")
    if report.extensions:
        lines.append("family_extensions:")
        lines.extend(_flatten_mapping_lines(report.extensions, prefix="  "))
    return lines


def _grc9v3_event_lane_summary(event_rows: Sequence[EventTelemetryRow]) -> Mapping[str, int]:
    counts: dict[str, int] = {}
    for event_row in event_rows:
        category = _event_visual_category(event_row)
        if category == "other":
            continue
        counts[category] = counts.get(category, 0) + 1
    return dict(sorted(counts.items()))


def _build_comparison_report_lines(report: TelemetryComparisonReport) -> list[str]:
    lines = [
        f"left_run_id: {report.common['left_run_id']}",
        f"right_run_id: {report.common['right_run_id']}",
        f"left_param_family: {report.common.get('left_param_family')}",
        f"right_param_family: {report.common.get('right_param_family')}",
        f"left_params_identity: {report.common.get('left_params_identity')}",
        f"right_params_identity: {report.common.get('right_params_identity')}",
        "final_observables_right_minus_left:",
    ]
    for key, value in sorted(report.common["final_observables_right_minus_left"].items()):
        lines.append(f"  {key}: {value}")
    if report.extensions:
        lines.append("family_extensions:")
        lines.extend(_flatten_mapping_lines(report.extensions, prefix="  "))
    return lines


def _render_text_panel(lines: Sequence[str], title: str, output_path: Path) -> None:
    _ensure_parent(output_path)
    figure, axis = plt.subplots(figsize=(10, max(4, 0.33 * len(lines))))
    axis.axis("off")
    axis.set_title(title, fontsize=14, loc="left")
    axis.text(
        0.01,
        0.98,
        "\n".join(lines),
        va="top",
        ha="left",
        family="monospace",
        fontsize=10,
        transform=axis.transAxes,
    )
    figure.tight_layout()
    figure.savefig(output_path, dpi=140)
    plt.close(figure)


def _create_grid(count: int, *, ncols: int, figsize: tuple[float, float]) -> tuple[Any, list[Any]]:
    figure, axes = plt.subplots(max(1, math.ceil(max(1, count) / ncols)), ncols, figsize=figsize)
    if not isinstance(axes, (list, tuple)):
        try:
            flattened = list(axes.flat)
        except AttributeError:
            flattened = [axes]
    else:
        flattened = list(axes)
    return figure, flattened


def _hide_unused_axes(axes: Sequence[Any]) -> None:
    for axis in axes:
        axis.axis("off")


def _trajectory_series(
    name: str,
    run_summary: RunTelemetrySummary,
    step_rows: Sequence[StepTelemetryRow],
) -> tuple[list[int], list[float]]:
    xs: list[int] = []
    ys: list[float] = []
    initial_value = _initial_series_value(name, run_summary)
    if _is_finite_number(initial_value):
        xs.append(0)
        ys.append(float(initial_value))
    for row in step_rows:
        value = _step_series_value(name, row)
        if _is_finite_number(value):
            xs.append(int(row.step_index))
            ys.append(float(value))
    return xs, ys


def _has_numeric_trajectory(
    name: str,
    run_summary: RunTelemetrySummary,
    step_rows: Sequence[StepTelemetryRow],
) -> bool:
    if _is_finite_number(_initial_series_value(name, run_summary)):
        return True
    return any(_is_finite_number(_step_series_value(name, row)) for row in step_rows)


def _initial_series_value(name: str, run_summary: RunTelemetrySummary) -> Any:
    if name.startswith("family_extensions."):
        return None
    return run_summary.initial_observables.get(name)


def _step_series_value(name: str, row: StepTelemetryRow) -> Any:
    if name.startswith("family_extensions."):
        value = _mapping_path_value(row.family_extensions, name.split(".")[1:])
        if (
            name.endswith(".last_candidate_column_h_branch_hit")
            or name.endswith(".column_h_branch_hit")
        ) and isinstance(value, bool):
            return float(value)
        return value
    return row.observables.get(name)


def _categorized_event_points(event_rows: Sequence[EventTelemetryRow]) -> list[tuple[int, str]]:
    points: list[tuple[int, str]] = []
    for event_row in event_rows:
        category = _event_visual_category(event_row)
        if category != "other":
            points.append((int(event_row.step_index), category))
    return points


def _event_visual_category(event_row: EventTelemetryRow) -> str:
    lgrc9v3_extension = event_row.family_extensions.get("lgrc9v3")
    if isinstance(lgrc9v3_extension, Mapping):
        domain = str(lgrc9v3_extension.get("event_domain", "other"))
        if domain == "packet":
            return "lgrc9v3_packet"
        if domain == "local_update":
            return "lgrc9v3_local_update"
        if domain == "topology":
            return "lgrc9v3_topology"
        if domain == "collapse":
            return "lgrc9v3_collapse"
        if domain == "identity":
            return "lgrc9v3_identity"
        if domain == "spark":
            evidence = _spark_evidence_payload(event_row)
            spark_lane = evidence.get("spark_lane")
            if spark_lane == "grc9v3_column_h_assisted":
                gate_reasons = tuple(
                    str(value) for value in _sequence_or_empty(evidence.get("gate_reasons"))
                )
                column_h_branch_hit = bool(evidence.get("column_h_branch_hit")) or any(
                    reason.startswith("column_h_") for reason in gate_reasons
                )
                if column_h_branch_hit:
                    return "lgrc9v3_lane_b_column_h_branch_candidate"
                return "lgrc9v3_lane_b_signed_hessian_candidate"
            return "lgrc9v3_lane_a_signed_hessian_candidate"
    if event_row.event_kind not in {
        "hybrid_spark_candidate",
        "lgrc9v3_causal_spark_candidate",
    }:
        return "other"
    evidence = _spark_evidence_payload(event_row)
    spark_lane = evidence.get("spark_lane")
    if spark_lane == "grc9v3_column_h_assisted":
        gate_reasons = tuple(str(value) for value in _sequence_or_empty(evidence.get("gate_reasons")))
        column_h_branch_hit = bool(evidence.get("column_h_branch_hit")) or any(
            reason.startswith("column_h_") for reason in gate_reasons
        )
        if column_h_branch_hit:
            return "lane_b_column_h_branch_candidate"
        return "lane_b_signed_hessian_candidate"
    return "lane_a_signed_hessian_candidate"


def _spark_evidence_payload(event_row: EventTelemetryRow) -> Mapping[str, Any]:
    lgrc9v3_extension = event_row.family_extensions.get("lgrc9v3")
    if isinstance(lgrc9v3_extension, Mapping):
        spark_fields = {
            "spark_lane",
            "gate_reasons",
            "column_h_branch_hit",
            "lane_b_candidate_hit",
        }
        if any(field in lgrc9v3_extension for field in spark_fields):
            return lgrc9v3_extension
    grc9v3_extension = event_row.family_extensions.get("grc9v3")
    if isinstance(grc9v3_extension, Mapping):
        spark_evidence = grc9v3_extension.get("spark_evidence")
        if isinstance(spark_evidence, Mapping):
            return spark_evidence
    return event_row.payload


def _event_category_color(category: str) -> str:
    colors = {
        "lane_a_signed_hessian_candidate": "#4c78a8",
        "lane_b_signed_hessian_candidate": "#f58518",
        "lane_b_column_h_branch_candidate": "#54a24b",
        "lgrc9v3_packet": "#4c78a8",
        "lgrc9v3_local_update": "#72b7b2",
        "lgrc9v3_lane_a_signed_hessian_candidate": "#9c755f",
        "lgrc9v3_lane_b_signed_hessian_candidate": "#ff9da6",
        "lgrc9v3_lane_b_column_h_branch_candidate": "#59a14f",
        "lgrc9v3_topology": "#b07aa1",
        "lgrc9v3_collapse": "#e15759",
        "lgrc9v3_identity": "#edc948",
    }
    return colors.get(category, "#d62728")


def _format_event_category(category: str) -> str:
    labels = {
        "lane_a_signed_hessian_candidate": "Lane A signed-H",
        "lane_b_signed_hessian_candidate": "Lane B signed-H",
        "lane_b_column_h_branch_candidate": "Lane B column-H",
        "lgrc9v3_packet": "LGRC packet",
        "lgrc9v3_local_update": "LGRC local update",
        "lgrc9v3_lane_a_signed_hessian_candidate": "LGRC Lane A signed-H",
        "lgrc9v3_lane_b_signed_hessian_candidate": "LGRC Lane B signed-H",
        "lgrc9v3_lane_b_column_h_branch_candidate": "LGRC Lane B column-H",
        "lgrc9v3_topology": "LGRC topology",
        "lgrc9v3_collapse": "LGRC collapse",
        "lgrc9v3_identity": "LGRC identity",
    }
    return labels.get(category, category.replace("_", " "))


def _mapping_path_value(root: Mapping[str, Any], path_parts: Sequence[str]) -> Any:
    current: Any = root
    for part in path_parts:
        if (
            part == "length"
            and isinstance(current, (Mapping, Sequence))
            and not isinstance(current, str | bytes)
        ):
            current = len(current)
            continue
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def _format_series_name(name: str) -> str:
    if name.startswith("family_extensions."):
        return name.removeprefix("family_extensions.")
    return name


def _trajectory_x_label(model_family: str) -> str:
    if _is_lgrc9v3_family(model_family):
        return "checkpoint/event row"
    return "step"


def _timeline_x_label(
    step_rows: Sequence[StepTelemetryRow],
    event_rows: Sequence[EventTelemetryRow],
) -> str:
    if step_rows and _is_lgrc9v3_family(step_rows[0].identity.model_family):
        return "checkpoint/event row"
    if event_rows and _is_lgrc9v3_family(event_rows[0].identity.model_family):
        return "checkpoint/event row"
    return "step"


def _is_lgrc9v3_family(model_family: str) -> bool:
    return model_family.lower() == "lgrc9v3"


def _flatten_mapping_lines(mapping: Mapping[str, Any], *, prefix: str) -> list[str]:
    lines: list[str] = []
    for key in sorted(mapping):
        value = mapping[key]
        if isinstance(value, Mapping):
            lines.extend(_flatten_mapping_lines(value, prefix=f"{prefix}{key}."))
        else:
            lines.append(f"{prefix}{key}: {value}")
    return lines


def _sequence_or_empty(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return value
    return ()


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


__all__ = [
    "DEFAULT_COMPARISON_OBSERVABLES",
    "DEFAULT_GRC9_COMPARISON_OBSERVABLES",
    "DEFAULT_GRC9_RUN_OBSERVABLES",
    "DEFAULT_GRC9V3_RUN_OBSERVABLES",
    "DEFAULT_LGRC9V3_RUN_OBSERVABLES",
    "DEFAULT_GRCV3_COMPARISON_OBSERVABLES",
    "DEFAULT_GRCV3_RUN_OBSERVABLES",
    "DEFAULT_RUN_OBSERVABLES",
    "_build_comparison_report_lines",
    "_build_run_report_lines",
    "_event_visual_category",
    "_grc9v3_event_lane_summary",
    "_trajectory_series",
    "render_comparison_visual_bundle",
    "render_run_visual_bundle",
]
