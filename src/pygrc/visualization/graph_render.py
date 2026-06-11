"""Artifact-driven graph rendering helpers for checkpoint-backed visuals."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/pygrc-matplotlib")

import matplotlib

matplotlib.use("Agg")

from matplotlib import colormaps
from matplotlib import colors as mpl_colors
from matplotlib import pyplot as plt
import networkx as nx
from PIL import Image
from pyvis.network import Network

from pygrc.core import canonical_json_dumps
from pygrc.telemetry import GraphCheckpointArtifact, TelemetryArtifactPack

from .layout import GraphComparisonVisualizationLayout, GraphRunVisualizationLayout


_LAYOUT_SEED = 17
_MAX_SEQUENCE_PANELS = 6
_NODE_SHAPE_BY_PRIMITIVE_TYPE: Mapping[str, str] = {
    "basin": "o",
    "plateau": "D",
    "junction": "s",
}


@dataclass(frozen=True)
class _GraphRenderContext:
    coherence_min: float
    coherence_max: float
    conductance_max: float
    flux_abs_max: float


_COLLAPSE_SOURCE_EDGE = "#d81b60"
_COLLAPSE_TARGET_EDGE = "#f9a825"
_CHOICE_EDGE = "#1e88e5"
_COLUMN_H_BRANCH_EDGE = "#2ca02c"
_LGRC9V3_PACKET_EDGE = "#00a6d6"
_LGRC9V3_TOPOLOGY_EDGE = "#7f3c8d"
_LGRC9V3_IDENTITY_EDGE = "#c49a00"


def render_graph_run_visual_bundle(
    pack: TelemetryArtifactPack,
    *,
    layout: GraphRunVisualizationLayout,
) -> GraphRunVisualizationLayout:
    """Render graph snapshots, contact sheet, interactive HTML, and animation."""

    checkpoints = _sorted_checkpoints(pack.graph_checkpoints)
    if not checkpoints:
        raise ValueError(
            "graph visualization requires saved graph checkpoints; rerun the experiment "
            "with record_graph_checkpoints=True"
        )

    layout.snapshots_dir.mkdir(parents=True, exist_ok=True)
    layout.html_dir.mkdir(parents=True, exist_ok=True)

    positions = _compute_union_layout(checkpoints)
    _write_layout_json(layout.layout_json_path, positions=positions, checkpoints=checkpoints)
    context = _build_render_context(checkpoints)

    snapshot_paths: list[Path] = []
    for checkpoint in checkpoints:
        snapshot_path = layout.snapshots_dir / _snapshot_filename(checkpoint)
        _render_graph_snapshot(
            checkpoint,
            positions=positions,
            context=context,
            output_path=snapshot_path,
        )
        snapshot_paths.append(snapshot_path)

    _render_graph_sequence_figure(
        checkpoints,
        positions=positions,
        context=context,
        output_path=layout.sequence_figure_path,
    )
    _render_final_graph_html(
        checkpoints[-1],
        positions=positions,
        context=context,
        output_path=layout.final_html_path,
    )
    if len(snapshot_paths) > 1:
        _render_animation(snapshot_paths, layout.animation_path)

    return layout


def render_graph_comparison_visual_bundle(
    left_pack: TelemetryArtifactPack,
    right_pack: TelemetryArtifactPack,
    *,
    layout: GraphComparisonVisualizationLayout,
) -> GraphComparisonVisualizationLayout:
    """Render one side-by-side final-checkpoint graph comparison figure."""

    left_checkpoints = _sorted_checkpoints(left_pack.graph_checkpoints)
    right_checkpoints = _sorted_checkpoints(right_pack.graph_checkpoints)
    if not left_checkpoints or not right_checkpoints:
        raise ValueError(
            "graph comparison requires saved graph checkpoints for both runs"
        )

    left_positions = _compute_union_layout(left_checkpoints)
    right_positions = _compute_union_layout(right_checkpoints)
    left_context = _build_render_context(left_checkpoints)
    right_context = _build_render_context(right_checkpoints)

    layout.final_comparison_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(1, 2, figsize=(14, 6))
    _draw_graph_checkpoint(
        axes[0],
        left_checkpoints[-1],
        positions=left_positions,
        context=left_context,
    )
    _draw_graph_checkpoint(
        axes[1],
        right_checkpoints[-1],
        positions=right_positions,
        context=right_context,
    )
    axes[0].set_title(
        f"{left_pack.run_summary.identity.seed_name or left_pack.run_summary.identity.run_id}\n"
        f"step={left_checkpoints[-1].step_index}",
        fontsize=11,
    )
    axes[1].set_title(
        f"{right_pack.run_summary.identity.seed_name or right_pack.run_summary.identity.run_id}\n"
        f"step={right_checkpoints[-1].step_index}",
        fontsize=11,
    )
    figure.suptitle("Representative graph comparison", fontsize=14)
    figure.tight_layout()
    figure.savefig(layout.final_comparison_path, dpi=140)
    plt.close(figure)
    return layout


def _sorted_checkpoints(
    checkpoints: Sequence[GraphCheckpointArtifact],
) -> tuple[GraphCheckpointArtifact, ...]:
    return tuple(
        sorted(
            checkpoints,
            key=lambda checkpoint: (
                checkpoint.step_index,
                checkpoint.time,
                checkpoint.checkpoint_label,
                checkpoint.checkpoint_id,
            ),
        )
    )


def _write_layout_json(
    output_path: Path,
    *,
    positions: Mapping[int, tuple[float, float]],
    checkpoints: Sequence[GraphCheckpointArtifact],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "layout_policy": "union_static_spring_or_large_graph_grid",
        "layout_seed": _LAYOUT_SEED,
        "node_positions": {
            str(node_id): {"x": round(float(x), 8), "y": round(float(y), 8)}
            for node_id, (x, y) in sorted(positions.items())
        },
        "checkpoint_ids": [checkpoint.checkpoint_id for checkpoint in checkpoints],
    }
    output_path.write_text(canonical_json_dumps(payload), encoding="utf-8")


def _compute_union_layout(
    checkpoints: Sequence[GraphCheckpointArtifact],
) -> dict[int, tuple[float, float]]:
    union_graph = nx.Graph()
    fixed_positions: dict[int, tuple[float, float]] = {}
    for checkpoint in checkpoints:
        for node_record in checkpoint.node_records:
            node_id = int(node_record["node_id"])
            union_graph.add_node(node_id)
            hint = _extract_chart_center_hint(node_record)
            if hint is not None and node_id not in fixed_positions:
                fixed_positions[node_id] = hint
        for edge_record in checkpoint.edge_records:
            source_node_id = int(edge_record["source_node_id"])
            target_node_id = int(edge_record["target_node_id"])
            union_graph.add_edge(source_node_id, target_node_id)

    node_ids = sorted(union_graph.nodes())
    if not node_ids:
        raise ValueError("graph checkpoint sequence contains no nodes")
    if len(node_ids) == 1:
        only_node = node_ids[0]
        return {only_node: fixed_positions.get(only_node, (0.0, 0.0))}
    if len(node_ids) >= 500:
        return _deterministic_large_graph_layout(
            node_ids=node_ids,
            fixed_positions=fixed_positions,
        )

    spring_kwargs = {
        "seed": _LAYOUT_SEED,
        "pos": fixed_positions or None,
        "fixed": sorted(fixed_positions) if fixed_positions else None,
        "iterations": 200,
    }
    try:
        spring_positions = nx.spring_layout(
            union_graph,
            method="force",
            **spring_kwargs,
        )
    except TypeError:
        spring_positions = nx.spring_layout(union_graph, **spring_kwargs)
    normalized = _normalize_positions(
        {int(node_id): (float(value[0]), float(value[1])) for node_id, value in spring_positions.items()}
    )
    for node_id, hint in fixed_positions.items():
        normalized[node_id] = hint
    return _normalize_positions(normalized)


def _deterministic_large_graph_layout(
    *,
    node_ids: Sequence[int],
    fixed_positions: Mapping[int, tuple[float, float]],
) -> dict[int, tuple[float, float]]:
    columns = max(1, int(math.ceil(math.sqrt(len(node_ids)))))
    positions: dict[int, tuple[float, float]] = {}
    for index, node_id in enumerate(node_ids):
        row, column = divmod(index, columns)
        positions[int(node_id)] = (float(column), float(-row))
    for node_id, hint in fixed_positions.items():
        positions[int(node_id)] = hint
    return _normalize_positions(positions)


def _normalize_positions(
    positions: Mapping[int, tuple[float, float]],
) -> dict[int, tuple[float, float]]:
    xs = [value[0] for value in positions.values()]
    ys = [value[1] for value in positions.values()]
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    span_x = max(max_x - min_x, 1e-9)
    span_y = max(max_y - min_y, 1e-9)
    span = max(span_x, span_y)
    center_x = 0.5 * (min_x + max_x)
    center_y = 0.5 * (min_y + max_y)
    normalized: dict[int, tuple[float, float]] = {}
    for node_id, (x_value, y_value) in positions.items():
        normalized[node_id] = (
            float((x_value - center_x) / span * 2.0),
            float((y_value - center_y) / span * 2.0),
        )
    return normalized


def _extract_chart_center_hint(node_record: Mapping[str, Any]) -> tuple[float, float] | None:
    payload = node_record.get("payload")
    if not isinstance(payload, Mapping):
        return None
    raw_center = payload.get("chart_center_hint")
    if not isinstance(raw_center, Sequence) or isinstance(raw_center, str | bytes):
        return None
    if len(raw_center) < 2:
        return None
    x_value = raw_center[0]
    y_value = raw_center[1]
    if not _is_finite_number(x_value) or not _is_finite_number(y_value):
        return None
    return (float(x_value), float(y_value))


def _build_render_context(
    checkpoints: Sequence[GraphCheckpointArtifact],
) -> _GraphRenderContext:
    coherence_values: list[float] = []
    conductance_values: list[float] = []
    flux_values: list[float] = []
    for checkpoint in checkpoints:
        for node_record in checkpoint.node_records:
            if _is_finite_number(node_record.get("coherence")):
                coherence_values.append(float(node_record["coherence"]))
        for edge_record in checkpoint.edge_records:
            if _is_finite_number(edge_record.get("base_conductance")):
                conductance_values.append(abs(float(edge_record["base_conductance"])))
            signed_flux = _edge_signed_flux(edge_record)
            if signed_flux is not None:
                flux_values.append(abs(signed_flux))
    coherence_min = min(coherence_values) if coherence_values else 0.0
    coherence_max = max(coherence_values) if coherence_values else 1.0
    if math.isclose(coherence_min, coherence_max):
        coherence_max = coherence_min + 1.0
    conductance_max = max(conductance_values) if conductance_values else 1.0
    flux_abs_max = max(flux_values) if flux_values else 0.0
    return _GraphRenderContext(
        coherence_min=coherence_min,
        coherence_max=coherence_max,
        conductance_max=max(conductance_max, 1e-9),
        flux_abs_max=max(flux_abs_max, 0.0),
    )


def _snapshot_filename(checkpoint: GraphCheckpointArtifact) -> str:
    safe_label = checkpoint.checkpoint_label.replace(" ", "_")
    return (
        f"step-{checkpoint.step_index:06d}"
        f"--time-{checkpoint.time:010.4f}"
        f"--{safe_label}.png"
    )


def _render_graph_snapshot(
    checkpoint: GraphCheckpointArtifact,
    *,
    positions: Mapping[int, tuple[float, float]],
    context: _GraphRenderContext,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(8, 6))
    _draw_graph_checkpoint(axis, checkpoint, positions=positions, context=context)
    figure.tight_layout()
    figure.savefig(output_path, dpi=140)
    plt.close(figure)


def _render_graph_sequence_figure(
    checkpoints: Sequence[GraphCheckpointArtifact],
    *,
    positions: Mapping[int, tuple[float, float]],
    context: _GraphRenderContext,
    output_path: Path,
) -> None:
    selected_indices = _sample_indices(len(checkpoints), max_panels=_MAX_SEQUENCE_PANELS)
    selected = [checkpoints[index] for index in selected_indices]
    ncols = min(3, len(selected))
    nrows = int(math.ceil(len(selected) / ncols))
    figure, axes = plt.subplots(nrows, ncols, figsize=(4.8 * ncols, 4.0 * nrows))
    axis_list = list(axes.flat) if hasattr(axes, "flat") else [axes]
    for axis, checkpoint in zip(axis_list, selected, strict=False):
        _draw_graph_checkpoint(axis, checkpoint, positions=positions, context=context)
    for axis in axis_list[len(selected) :]:
        axis.axis("off")
    figure.suptitle("Graph checkpoint sequence", fontsize=14)
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=140)
    plt.close(figure)


def _sample_indices(count: int, *, max_panels: int) -> list[int]:
    if count <= max_panels:
        return list(range(count))
    indices: list[int] = []
    for panel_index in range(max_panels):
        scaled = round(panel_index * (count - 1) / (max_panels - 1))
        if not indices or scaled != indices[-1]:
            indices.append(int(scaled))
    while len(indices) < max_panels:
        indices.append(count - 1)
    return indices


def _draw_graph_checkpoint(
    axis: Any,
    checkpoint: GraphCheckpointArtifact,
    *,
    positions: Mapping[int, tuple[float, float]],
    context: _GraphRenderContext,
) -> None:
    graph = nx.Graph()
    node_records_by_id = {
        int(node_record["node_id"]): node_record for node_record in checkpoint.node_records
    }
    for node_id, record in node_records_by_id.items():
        graph.add_node(node_id, record=record)
    for edge_record in checkpoint.edge_records:
        source_node_id = int(edge_record["source_node_id"])
        target_node_id = int(edge_record["target_node_id"])
        graph.add_edge(source_node_id, target_node_id, record=edge_record)

    checkpoint_positions = {node_id: positions[node_id] for node_id in graph.nodes()}
    edge_items = list(graph.edges(data=True))
    structural_edge_colors = [
        _structural_edge_color(edge_data["record"], context=context)
        for _, _, edge_data in edge_items
    ]
    structural_edge_widths = [
        _structural_edge_width(edge_data["record"], context=context)
        for _, _, edge_data in edge_items
    ]
    nx.draw_networkx_edges(
        graph,
        pos=checkpoint_positions,
        ax=axis,
        edge_color=structural_edge_colors,
        width=structural_edge_widths,
        alpha=0.55,
    )
    _draw_flow_overlays(
        axis,
        checkpoint,
        positions=checkpoint_positions,
        context=context,
    )
    _draw_lgrc9v3_packet_overlays(
        axis,
        checkpoint,
        positions=checkpoint_positions,
    )
    _draw_lgrc9v3_topology_lineage_overlays(
        axis,
        checkpoint,
        positions=checkpoint_positions,
    )
    _draw_collapse_overlays(
        axis,
        checkpoint,
        positions=checkpoint_positions,
    )

    for primitive_type, node_shape in _NODE_SHAPE_BY_PRIMITIVE_TYPE.items():
        node_ids = [
            node_id
            for node_id, record in node_records_by_id.items()
            if _primitive_type(record) == primitive_type
        ]
        if node_ids:
            nx.draw_networkx_nodes(
                graph,
                pos=checkpoint_positions,
                nodelist=node_ids,
                node_color=[
                    _node_color(node_records_by_id[node_id], context=context) for node_id in node_ids
                ],
                node_size=[
                    _node_size(node_records_by_id[node_id], context=context) for node_id in node_ids
                ],
                node_shape=node_shape,
                linewidths=[
                    _node_linewidth(node_records_by_id[node_id], checkpoint=checkpoint)
                    for node_id in node_ids
                ],
                edgecolors=[
                    _node_edgecolor(node_records_by_id[node_id], checkpoint=checkpoint)
                    for node_id in node_ids
                ],
                ax=axis,
            )

    remaining_node_ids = [
        node_id
        for node_id, record in node_records_by_id.items()
        if _primitive_type(record) not in _NODE_SHAPE_BY_PRIMITIVE_TYPE
    ]
    if remaining_node_ids:
        nx.draw_networkx_nodes(
            graph,
            pos=checkpoint_positions,
            nodelist=remaining_node_ids,
            node_color=[
                _node_color(node_records_by_id[node_id], context=context)
                for node_id in remaining_node_ids
            ],
            node_size=[
                _node_size(node_records_by_id[node_id], context=context)
                for node_id in remaining_node_ids
            ],
            node_shape="o",
            linewidths=[
                _node_linewidth(node_records_by_id[node_id], checkpoint=checkpoint)
                for node_id in remaining_node_ids
            ],
            edgecolors=[
                _node_edgecolor(node_records_by_id[node_id], checkpoint=checkpoint)
                for node_id in remaining_node_ids
            ],
            ax=axis,
        )

    if graph.number_of_nodes() <= 40:
        nx.draw_networkx_labels(
            graph,
            pos=checkpoint_positions,
            labels={
                node_id: _node_label(node_records_by_id[node_id], checkpoint=checkpoint)
                for node_id in graph.nodes()
                if node_id in node_records_by_id
            },
            font_size=7,
            ax=axis,
        )

    axis.set_xlim(-1.15, 1.15)
    axis.set_ylim(-1.15, 1.15)
    axis.set_axis_off()
    subtitle = _checkpoint_subtitle(checkpoint)
    axis.set_title(subtitle, fontsize=10)


def _checkpoint_subtitle(checkpoint: GraphCheckpointArtifact) -> str:
    event_suffix = ""
    if checkpoint.event_count_window > 0:
        event_suffix = f"\nevent_window={checkpoint.event_count_window}"
    collapse_count = 0
    if isinstance(checkpoint.event_counts_by_kind_window, Mapping):
        raw_collapse_count = checkpoint.event_counts_by_kind_window.get("collapse", 0)
        if isinstance(raw_collapse_count, int):
            collapse_count = raw_collapse_count
    collapse_suffix = f"  collapse={collapse_count}" if collapse_count > 0 else ""
    lgrc_suffix = _lgrc9v3_checkpoint_subtitle(checkpoint)
    return (
        f"step={checkpoint.step_index}  t={checkpoint.time:.3f}  "
        f"nodes={checkpoint.node_count}  edges={checkpoint.edge_count}"
        f"{collapse_suffix}{event_suffix}{lgrc_suffix}"
    )


def _lgrc9v3_checkpoint_subtitle(checkpoint: GraphCheckpointArtifact) -> str:
    extension = _lgrc9v3_extension(checkpoint)
    if not extension:
        return ""
    clocks = extension.get("causal_clocks", {})
    packet_ledger = extension.get("packet_ledger", {})
    topology_history = extension.get("topology_history", {})
    if not isinstance(clocks, Mapping):
        clocks = {}
    if not isinstance(packet_ledger, Mapping):
        packet_ledger = {}
    if not isinstance(topology_history, Mapping):
        topology_history = {}
    return (
        "\n"
        f"kappa={clocks.get('scheduler_event_index')}  "
        f"k={clocks.get('checkpoint_index')}  "
        f"T_e={clocks.get('event_time_key')}  "
        f"in_flight={packet_ledger.get('in_flight_packet_total')}  "
        f"topology_events={topology_history.get('topology_event_count')}"
    )


def _primitive_type(node_record: Mapping[str, Any]) -> str:
    payload = node_record.get("payload")
    if isinstance(payload, Mapping):
        primitive_type = payload.get("primitive_type")
        if isinstance(primitive_type, str):
            return primitive_type
    return ""


def _node_color(node_record: Mapping[str, Any], *, context: _GraphRenderContext) -> str:
    value = float(node_record.get("coherence", 0.0))
    normalized = (value - context.coherence_min) / (context.coherence_max - context.coherence_min)
    rgba = colormaps["viridis"](min(max(normalized, 0.0), 1.0))
    if _node_is_collapsed_inactive(node_record):
        rgba = (rgba[0], rgba[1], rgba[2], 0.28)
        return mpl_colors.to_hex(rgba, keep_alpha=True)
    return mpl_colors.to_hex(rgba)


def _node_size(node_record: Mapping[str, Any], *, context: _GraphRenderContext) -> float:
    value = float(node_record.get("coherence", 0.0))
    normalized = (value - context.coherence_min) / (context.coherence_max - context.coherence_min)
    return 260.0 + 900.0 * min(max(normalized, 0.0), 1.0)


def _node_linewidth(
    node_record: Mapping[str, Any], *, checkpoint: GraphCheckpointArtifact
) -> float:
    if _node_has_column_h_branch(node_record, checkpoint=checkpoint):
        return 3.4
    if _node_has_lgrc9v3_identity_acceptance(node_record, checkpoint=checkpoint):
        return 3.1
    if bool(node_record.get("choice_flag")):
        return 2.4
    if bool(node_record.get("collapse_flag")):
        return 3.2
    if bool(node_record.get("sink_flag")) or bool(node_record.get("is_sink")):
        return 2.2
    return 1.0


def _node_edgecolor(
    node_record: Mapping[str, Any], *, checkpoint: GraphCheckpointArtifact
) -> str:
    if _node_has_column_h_branch(node_record, checkpoint=checkpoint):
        return _COLUMN_H_BRANCH_EDGE
    if _node_has_lgrc9v3_identity_acceptance(node_record, checkpoint=checkpoint):
        return _LGRC9V3_IDENTITY_EDGE
    if bool(node_record.get("choice_flag")):
        return _CHOICE_EDGE
    if _node_is_collapsed_inactive(node_record):
        return _COLLAPSE_SOURCE_EDGE
    node_id = str(node_record.get("node_id"))
    if node_id in _collapse_target_ids(checkpoint):
        return _COLLAPSE_TARGET_EDGE
    if bool(node_record.get("sink_flag")) or bool(node_record.get("is_sink")):
        return "#111111"
    return "#666666"


def _edge_color(edge_record: Mapping[str, Any], *, context: _GraphRenderContext) -> str:
    signed_flux = _edge_signed_flux(edge_record)
    if context.flux_abs_max > 0.0 and signed_flux is not None:
        value = signed_flux
        normalized = (value + context.flux_abs_max) / (2.0 * context.flux_abs_max)
        rgba = colormaps["coolwarm"](min(max(normalized, 0.0), 1.0))
        return mpl_colors.to_hex(rgba)
    return _structural_edge_color(edge_record, context=context)


def _edge_width(edge_record: Mapping[str, Any], *, context: _GraphRenderContext) -> float:
    structural_width = _structural_edge_width(edge_record, context=context)
    signed_flux = _edge_signed_flux(edge_record)
    if context.flux_abs_max > 0.0 and signed_flux is not None:
        flux_value = abs(signed_flux)
        flux_normalized = min(max(flux_value / context.flux_abs_max, 0.0), 1.0)
        return structural_width + 0.9 + 4.2 * flux_normalized
    return structural_width


def _structural_edge_color(
    edge_record: Mapping[str, Any], *, context: _GraphRenderContext
) -> str:
    value = abs(float(edge_record.get("base_conductance", 0.0)))
    normalized = min(max(value / context.conductance_max, 0.0), 1.0)
    rgba = colormaps["Greys"](0.30 + 0.40 * normalized)
    return mpl_colors.to_hex(rgba)


def _structural_edge_width(
    edge_record: Mapping[str, Any], *, context: _GraphRenderContext
) -> float:
    value = abs(float(edge_record.get("base_conductance", 0.0)))
    normalized = min(max(value / context.conductance_max, 0.0), 1.0)
    return 0.7 + 2.1 * normalized


def _draw_flow_overlays(
    axis: Any,
    checkpoint: GraphCheckpointArtifact,
    *,
    positions: Mapping[int, tuple[float, float]],
    context: _GraphRenderContext,
) -> None:
    if context.flux_abs_max <= 0.0:
        return
    flow_graph = nx.DiGraph()
    edge_colors: list[str] = []
    edge_widths: list[float] = []
    arrowsizes: list[float] = []
    for edge_record in checkpoint.edge_records:
        directed_endpoints = _directed_edge_endpoints(edge_record)
        if directed_endpoints is None:
            continue
        source_node_id, target_node_id = directed_endpoints
        flow_graph.add_edge(source_node_id, target_node_id, record=edge_record)
        edge_colors.append(_edge_color(edge_record, context=context))
        edge_widths.append(_edge_width(edge_record, context=context))
        arrowsizes.append(_edge_arrow_size(edge_record, context=context))
    if flow_graph.number_of_edges() == 0:
        return
    nx.draw_networkx_edges(
        flow_graph,
        pos=positions,
        ax=axis,
        edge_color=edge_colors,
        width=edge_widths,
        alpha=0.95,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=arrowsizes,
        connectionstyle="arc3,rad=0.03",
        min_source_margin=6,
        min_target_margin=10,
    )


def _draw_collapse_overlays(
    axis: Any,
    checkpoint: GraphCheckpointArtifact,
    *,
    positions: Mapping[int, tuple[float, float]],
) -> None:
    collapse_edges: list[tuple[int, int]] = []
    for node_record in checkpoint.node_records:
        if not _node_is_collapsed_inactive(node_record):
            continue
        collapsed_sink_id = node_record.get("collapsed_sink_id")
        if not _is_int_like(collapsed_sink_id):
            continue
        source_node_id = int(node_record["node_id"])
        target_node_id = int(collapsed_sink_id)
        if source_node_id not in positions or target_node_id not in positions:
            continue
        collapse_edges.append((source_node_id, target_node_id))
    if not collapse_edges:
        return
    collapse_graph = nx.DiGraph()
    collapse_graph.add_edges_from(collapse_edges)
    nx.draw_networkx_edges(
        collapse_graph,
        pos=positions,
        ax=axis,
        edge_color=_COLLAPSE_SOURCE_EDGE,
        width=2.8,
        alpha=0.85,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=22,
        style="dashed",
        connectionstyle="arc3,rad=-0.12",
        min_source_margin=16,
        min_target_margin=18,
    )


def _draw_lgrc9v3_packet_overlays(
    axis: Any,
    checkpoint: GraphCheckpointArtifact,
    *,
    positions: Mapping[int, tuple[float, float]],
) -> None:
    packet_edges: list[tuple[int, int]] = []
    edge_widths: list[float] = []
    for packet in _lgrc9v3_packet_records(checkpoint):
        if str(packet.get("packet_state")) != "in_flight":
            continue
        source_node_id = packet.get("source_node_id")
        target_node_id = packet.get("target_node_id")
        if not _is_int_like(source_node_id) or not _is_int_like(target_node_id):
            continue
        source_id = int(source_node_id)
        target_id = int(target_node_id)
        if source_id not in positions or target_id not in positions:
            continue
        packet_edges.append((source_id, target_id))
        amount = packet.get("amount", 0.0)
        if _is_finite_number(amount):
            normalized_amount = min(max(float(amount), 0.0), 1.0)
            edge_widths.append(1.8 + 3.0 * normalized_amount)
        else:
            edge_widths.append(2.0)
    if not packet_edges:
        return
    packet_graph = nx.DiGraph()
    packet_graph.add_edges_from(packet_edges)
    nx.draw_networkx_edges(
        packet_graph,
        pos=positions,
        ax=axis,
        edge_color=_LGRC9V3_PACKET_EDGE,
        width=edge_widths,
        alpha=0.9,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=20,
        style="dotted",
        connectionstyle="arc3,rad=0.18",
        min_source_margin=16,
        min_target_margin=18,
    )


def _draw_lgrc9v3_topology_lineage_overlays(
    axis: Any,
    checkpoint: GraphCheckpointArtifact,
    *,
    positions: Mapping[int, tuple[float, float]],
) -> None:
    lineage_edges = _lgrc9v3_topology_lineage_edges(checkpoint, positions=positions)
    if not lineage_edges:
        return
    lineage_graph = nx.DiGraph()
    lineage_graph.add_edges_from(lineage_edges)
    nx.draw_networkx_edges(
        lineage_graph,
        pos=positions,
        ax=axis,
        edge_color=_LGRC9V3_TOPOLOGY_EDGE,
        width=2.4,
        alpha=0.82,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=18,
        style="dashdot",
        connectionstyle="arc3,rad=-0.16",
        min_source_margin=14,
        min_target_margin=16,
    )


def _directed_edge_endpoints(
    edge_record: Mapping[str, Any],
) -> tuple[int, int] | None:
    signed_flux = _edge_signed_flux(edge_record)
    if signed_flux is None:
        return None
    source_node_id = int(edge_record["source_node_id"])
    target_node_id = int(edge_record["target_node_id"])
    if math.isclose(signed_flux, 0.0):
        return None
    if signed_flux > 0.0:
        return (source_node_id, target_node_id)
    return (target_node_id, source_node_id)


def _edge_arrow_size(edge_record: Mapping[str, Any], *, context: _GraphRenderContext) -> float:
    signed_flux = _edge_signed_flux(edge_record)
    if context.flux_abs_max <= 0.0 or signed_flux is None:
        return 14.0
    flux_value = abs(signed_flux)
    flux_normalized = min(max(flux_value / context.flux_abs_max, 0.0), 1.0)
    return 16.0 + 18.0 * flux_normalized


def _render_final_graph_html(
    checkpoint: GraphCheckpointArtifact,
    *,
    positions: Mapping[int, tuple[float, float]],
    context: _GraphRenderContext,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    network = Network(
        height="720px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#222222",
    )
    network.toggle_physics(False)

    for node_record in checkpoint.node_records:
        node_id = int(node_record["node_id"])
        x_value, y_value = positions[node_id]
        border_width = _node_linewidth(node_record, checkpoint=checkpoint)
        border_color = _node_edgecolor(node_record, checkpoint=checkpoint)
        network.add_node(
            node_id,
            label=_node_label(node_record, checkpoint=checkpoint),
            x=float(x_value * 350.0),
            y=float(-y_value * 350.0),
            physics=False,
            shape=_pyvis_shape(node_record),
            size=max(12.0, _node_size(node_record, context=context) / 55.0),
            borderWidth=border_width,
            color={
                "background": _node_color(node_record, context=context),
                "border": border_color,
                "highlight": {
                    "background": _node_color(node_record, context=context),
                    "border": border_color,
                },
            },
            title=_node_title(node_record, checkpoint=checkpoint),
        )

    for edge_record in checkpoint.edge_records:
        directed_endpoints = _directed_edge_endpoints(edge_record)
        if directed_endpoints is None:
            source_node_id = int(edge_record["source_node_id"])
            target_node_id = int(edge_record["target_node_id"])
            edge_kwargs: dict[str, Any] = {}
        else:
            source_node_id, target_node_id = directed_endpoints
            edge_kwargs = {"arrows": "to"}
        network.add_edge(
            source_node_id,
            target_node_id,
            color=_edge_color(edge_record, context=context),
            width=_edge_width(edge_record, context=context),
            title=_edge_title(edge_record, checkpoint=checkpoint),
            **edge_kwargs,
        )
    for source_node_id, target_node_id in _lgrc9v3_topology_lineage_edges(
        checkpoint,
        positions=positions,
    ):
        network.add_edge(
            int(source_node_id),
            int(target_node_id),
            color={"color": _LGRC9V3_TOPOLOGY_EDGE, "highlight": _LGRC9V3_TOPOLOGY_EDGE},
            width=2.2,
            title="lgrc9v3_topology_lineage=true",
            arrows="to",
            dashes=True,
            physics=False,
            smooth={"enabled": True, "type": "curvedCCW", "roundness": 0.2},
        )
    for packet in _lgrc9v3_packet_records(checkpoint):
        if str(packet.get("packet_state")) != "in_flight":
            continue
        source_node_id = packet.get("source_node_id")
        target_node_id = packet.get("target_node_id")
        if not _is_int_like(source_node_id) or not _is_int_like(target_node_id):
            continue
        network.add_edge(
            int(source_node_id),
            int(target_node_id),
            color={"color": _LGRC9V3_PACKET_EDGE, "highlight": _LGRC9V3_PACKET_EDGE},
            width=2.4,
            title=_lgrc9v3_packet_title(packet),
            arrows="to",
            dashes=True,
            physics=False,
            smooth={"enabled": True, "type": "curvedCW", "roundness": 0.24},
        )
    for node_record in checkpoint.node_records:
        if not _node_is_collapsed_inactive(node_record):
            continue
        collapsed_sink_id = node_record.get("collapsed_sink_id")
        if not _is_int_like(collapsed_sink_id):
            continue
        network.add_edge(
            int(node_record["node_id"]),
            int(collapsed_sink_id),
            color={"color": _COLLAPSE_SOURCE_EDGE, "highlight": _COLLAPSE_SOURCE_EDGE},
            width=3.0,
            title=_collapse_edge_title(node_record),
            arrows="to",
            dashes=True,
            physics=False,
            smooth={"enabled": True, "type": "curvedCW", "roundness": 0.18},
        )

    network.write_html(str(output_path), notebook=False, open_browser=False)


def _pyvis_shape(node_record: Mapping[str, Any]) -> str:
    primitive_type = _primitive_type(node_record)
    if primitive_type == "junction":
        return "square"
    if primitive_type == "plateau":
        return "diamond"
    return "dot"


def _node_label(
    node_record: Mapping[str, Any], *, checkpoint: GraphCheckpointArtifact
) -> str:
    label = str(node_record.get("node_id"))
    if _node_has_column_h_branch(node_record, checkpoint=checkpoint):
        return f"{label}\nH"
    return label


def _node_title(
    node_record: Mapping[str, Any], *, checkpoint: GraphCheckpointArtifact | None = None
) -> str:
    payload = node_record.get("payload", {})
    parts = [
        f"node_id={node_record.get('node_id')}",
        f"coherence={node_record.get('coherence')}",
    ]
    if node_record.get("sink_flag"):
        parts.append("sink=true")
    if node_record.get("is_sink"):
        parts.append("is_sink=true")
    if "basin_id" in node_record:
        parts.append(f"basin_id={node_record['basin_id']}")
    if "parent_id" in node_record:
        parts.append(f"parent_id={node_record['parent_id']}")
    if "depth" in node_record:
        parts.append(f"depth={node_record['depth']}")
    if "node_proper_time" in node_record:
        parts.append(f"node_proper_time={node_record['node_proper_time']}")
    if "node_last_update_proper_time" in node_record:
        parts.append(
            "node_last_update_proper_time="
            + str(node_record["node_last_update_proper_time"])
        )
    if "node_last_update_event_time_key" in node_record:
        parts.append(
            "node_last_update_event_time_key="
            + str(node_record["node_last_update_event_time_key"])
        )
    if "lapse" in node_record:
        parts.append(f"lapse={node_record['lapse']}")
    if "active_degree" in node_record:
        parts.append(f"active_degree={node_record['active_degree']}")
    if "potential" in node_record:
        parts.append(f"potential={node_record['potential']}")
    if node_record.get("choice_flag"):
        viable_sink_ids = node_record.get("choice_viable_sink_ids")
        if viable_sink_ids is not None:
            parts.append(f"choice_viable_sink_ids={viable_sink_ids}")
        if "choice_winner_sink_id" in node_record:
            parts.append(f"choice_winner_sink_id={node_record['choice_winner_sink_id']}")
        if "choice_winner_margin" in node_record:
            parts.append(f"choice_winner_margin={node_record['choice_winner_margin']}")
    if node_record.get("collapse_flag"):
        if "collapsed_sink_id" in node_record:
            parts.append(f"collapsed_sink_id={node_record['collapsed_sink_id']}")
        if "collapse_winner_margin" in node_record:
            parts.append(f"collapse_winner_margin={node_record['collapse_winner_margin']}")
        if "collapsed_step_index" in node_record:
            parts.append(f"collapsed_step_index={node_record['collapsed_step_index']}")
        previous_viable_sink_ids = node_record.get("previous_viable_sink_ids")
        if previous_viable_sink_ids is not None:
            parts.append(f"previous_viable_sink_ids={previous_viable_sink_ids}")
    if str(node_record.get("node_id")) in _collapse_target_ids_from_node_record(node_record):
        parts.append("collapse_target=true")
    lane_b_overlay = (
        _node_overlay_record(node_record, checkpoint=checkpoint)
        if checkpoint is not None
        else {}
    )
    if bool(lane_b_overlay.get("column_h_branch_hit")) or bool(
        node_record.get("column_h_branch_hit")
    ):
        parts.append("column_h_branch_hit=true")
    if "spark_lane" in lane_b_overlay:
        parts.append(f"spark_lane={lane_b_overlay['spark_lane']}")
    if "min_abs_column_h" in lane_b_overlay:
        parts.append(f"min_abs_column_h={lane_b_overlay['min_abs_column_h']}")
    if "column_h_gate_reasons" in lane_b_overlay:
        parts.append(f"column_h_gate_reasons={lane_b_overlay['column_h_gate_reasons']}")
    identity_evidence = _lgrc9v3_identity_evidence_for_node(node_record, checkpoint=checkpoint)
    if identity_evidence:
        parts.append("lgrc9v3_identity_acceptance=true")
        for key in (
            "identity_clock_policy",
            "observed_persistence_duration",
            "proper_time_persistence_threshold",
        ):
            if key in identity_evidence:
                parts.append(f"{key}={identity_evidence[key]}")
    if isinstance(payload, Mapping):
        primitive_id = payload.get("primitive_id")
        primitive_type = payload.get("primitive_type")
        role = payload.get("role")
        if primitive_id is not None:
            parts.append(f"primitive_id={primitive_id}")
        if primitive_type is not None:
            parts.append(f"primitive_type={primitive_type}")
        if role is not None:
            parts.append(f"role={role}")
        if payload.get("is_hostless") is True:
            parts.append("hostless=true")
    top_level_role = node_record.get("role")
    if top_level_role is not None:
        parts.append(f"role={top_level_role}")
    return "<br>".join(parts)


def _node_has_column_h_branch(
    node_record: Mapping[str, Any], *, checkpoint: GraphCheckpointArtifact
) -> bool:
    if bool(node_record.get("column_h_branch_hit")):
        return True
    payload = node_record.get("payload")
    if isinstance(payload, Mapping) and bool(payload.get("column_h_branch_hit")):
        return True
    return bool(
        _node_overlay_record(node_record, checkpoint=checkpoint).get(
            "column_h_branch_hit"
        )
    )


def _node_overlay_record(
    node_record: Mapping[str, Any], *, checkpoint: GraphCheckpointArtifact | None
) -> Mapping[str, Any]:
    if checkpoint is None:
        return {}
    node_id = str(node_record.get("node_id"))
    grc9v3_extension = checkpoint.family_extensions.get("grc9v3")
    if not isinstance(grc9v3_extension, Mapping):
        return {}
    node_overlay = grc9v3_extension.get("node_overlay")
    if not isinstance(node_overlay, Mapping):
        return {}
    overlay_record = node_overlay.get(node_id)
    if isinstance(overlay_record, Mapping):
        return overlay_record
    return {}


def _collapse_edge_title(node_record: Mapping[str, Any]) -> str:
    parts = [
        f"collapse_source_node_id={node_record.get('node_id')}",
        f"collapsed_sink_id={node_record.get('collapsed_sink_id')}",
    ]
    if "collapse_winner_margin" in node_record:
        parts.append(f"winner_margin={node_record['collapse_winner_margin']}")
    if "collapsed_step_index" in node_record:
        parts.append(f"collapsed_step_index={node_record['collapsed_step_index']}")
    return "<br>".join(parts)


def _edge_title(
    edge_record: Mapping[str, Any], *, checkpoint: GraphCheckpointArtifact | None = None
) -> str:
    parts = [
        f"edge_id={edge_record.get('edge_id')}",
        f"conductance={edge_record.get('base_conductance')}",
    ]
    if "landscape_base_conductance" in edge_record:
        parts.append(
            "landscape_base_conductance="
            + str(edge_record.get("landscape_base_conductance"))
        )
    if "transport_intent_multiplier" in edge_record:
        parts.append(
            "transport_intent_multiplier="
            + str(edge_record.get("transport_intent_multiplier"))
        )
    if "signed_flux_source" in edge_record:
        parts.append("signed_flux_source=" + str(edge_record.get("signed_flux_source")))
    if "signed_flux_source_to_target" in edge_record:
        parts.append(
            "signed_flux_source_to_target="
            + str(edge_record.get("signed_flux_source_to_target"))
        )
    if "geometric_length" in edge_record:
        parts.append("geometric_length=" + str(edge_record.get("geometric_length")))
    if "temporal_delay" in edge_record:
        parts.append("temporal_delay=" + str(edge_record.get("temporal_delay")))
    if "edge_causal_delay" in edge_record:
        parts.append("edge_causal_delay=" + str(edge_record.get("edge_causal_delay")))
    if checkpoint is not None:
        packet_summary = _lgrc9v3_packet_summary_for_edge(edge_record, checkpoint=checkpoint)
        if packet_summary:
            parts.extend(packet_summary)
    if edge_record.get("geometric_length_available") is False:
        parts.append("geometric_length=not_available")
    directionality_semantics = edge_record.get("directionality_semantics")
    if directionality_semantics is not None:
        parts.append("directionality_semantics=" + str(directionality_semantics))
    return "<br>".join(parts)


def _render_animation(frame_paths: Sequence[Path], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    images: list[Image.Image] = []
    try:
        for path in frame_paths:
            with Image.open(path) as raw_image:
                images.append(raw_image.convert("P", palette=Image.ADAPTIVE))
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            duration=350,
            loop=0,
            optimize=False,
            disposal=2,
        )
    finally:
        for image in images:
            image.close()


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value)


def _edge_signed_flux(edge_record: Mapping[str, Any]) -> float | None:
    for field_name in ("signed_flux_source", "signed_flux_source_to_target", "flux_uv"):
        value = edge_record.get(field_name)
        if _is_finite_number(value):
            return float(value)
    return None


def _lgrc9v3_extension(checkpoint: GraphCheckpointArtifact | None) -> Mapping[str, Any]:
    if checkpoint is None:
        return {}
    extension = checkpoint.family_extensions.get("lgrc9v3")
    if isinstance(extension, Mapping):
        return extension
    return {}


def _lgrc9v3_packet_records(checkpoint: GraphCheckpointArtifact | None) -> tuple[Mapping[str, Any], ...]:
    extension = _lgrc9v3_extension(checkpoint)
    packet_ledger = extension.get("packet_ledger")
    if not isinstance(packet_ledger, Mapping):
        return ()
    records = packet_ledger.get("packet_records", ())
    if not isinstance(records, Sequence) or isinstance(records, str | bytes):
        return ()
    return tuple(record for record in records if isinstance(record, Mapping))


def _lgrc9v3_packet_summary_for_edge(
    edge_record: Mapping[str, Any], *, checkpoint: GraphCheckpointArtifact
) -> list[str]:
    edge_id = edge_record.get("edge_id")
    if not _is_int_like(edge_id):
        return []
    packets = [
        packet
        for packet in _lgrc9v3_packet_records(checkpoint)
        if _is_int_like(packet.get("edge_id")) and int(packet["edge_id"]) == int(edge_id)
    ]
    if not packets:
        return []
    in_flight = [
        packet for packet in packets if str(packet.get("packet_state")) == "in_flight"
    ]
    amount_total = sum(
        float(packet.get("amount", 0.0))
        for packet in in_flight
        if _is_finite_number(packet.get("amount"))
    )
    return [
        f"lgrc9v3_packet_count={len(packets)}",
        f"lgrc9v3_in_flight_packet_count={len(in_flight)}",
        f"lgrc9v3_in_flight_packet_amount={amount_total}",
    ]


def _lgrc9v3_packet_title(packet: Mapping[str, Any]) -> str:
    parts = [
        "lgrc9v3_packet=true",
        f"packet_id={packet.get('packet_id')}",
        f"packet_state={packet.get('packet_state')}",
        f"amount={packet.get('amount')}",
        f"T_depart={packet.get('departure_event_time_key')}",
        f"T_arrive={packet.get('arrival_event_time_key')}",
    ]
    return "<br>".join(parts)


def _lgrc9v3_topology_history_events(
    checkpoint: GraphCheckpointArtifact | None,
) -> tuple[Mapping[str, Any], ...]:
    extension = _lgrc9v3_extension(checkpoint)
    topology_history = extension.get("topology_history")
    if not isinstance(topology_history, Mapping):
        return ()
    records = topology_history.get("topology_event_log", ())
    if not isinstance(records, Sequence) or isinstance(records, str | bytes):
        return ()
    return tuple(record for record in records if isinstance(record, Mapping))


def _event_payload_from_history_record(record: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = record.get("payload")
    if isinstance(payload, Mapping):
        return payload
    return record


def _lgrc9v3_topology_lineage_edges(
    checkpoint: GraphCheckpointArtifact,
    *,
    positions: Mapping[int, tuple[float, float]],
) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for record in _lgrc9v3_topology_history_events(checkpoint):
        payload = _event_payload_from_history_record(record)
        parent_node_id = payload.get("parent_node_id")
        child_node_id = payload.get("child_node_id")
        if _is_int_like(parent_node_id) and _is_int_like(child_node_id):
            parent_id = int(parent_node_id)
            child_id = int(child_node_id)
            if parent_id in positions and child_id in positions:
                edges.append((parent_id, child_id))
        expanded_node_id = payload.get("expanded_node_id", payload.get("sink_node_id"))
        replacements = payload.get("replacement_node_ids", payload.get("module_node_ids", ()))
        if _is_int_like(expanded_node_id) and isinstance(replacements, Sequence) and not isinstance(replacements, str | bytes):
            source_id = int(expanded_node_id)
            for replacement in replacements:
                if not _is_int_like(replacement):
                    continue
                target_id = int(replacement)
                if source_id in positions and target_id in positions:
                    edges.append((source_id, target_id))
    return sorted(set(edges))


def _lgrc9v3_identity_evidence_for_node(
    node_record: Mapping[str, Any], *, checkpoint: GraphCheckpointArtifact | None
) -> Mapping[str, Any]:
    node_id = node_record.get("node_id")
    if not _is_int_like(node_id):
        return {}
    resolved_node_id = int(node_id)
    for record in _lgrc9v3_topology_history_events(checkpoint):
        kind = str(record.get("kind", ""))
        payload = _event_payload_from_history_record(record)
        topology_event_kind = str(payload.get("topology_event_kind", ""))
        if (
            kind != "lgrc9v3_proper_time_identity_acceptance"
            and topology_event_kind != "lgrc9v3_proper_time_identity_acceptance"
        ):
            continue
        sink_node_id = payload.get("sink_node_id")
        if _is_int_like(sink_node_id) and int(sink_node_id) == resolved_node_id:
            return payload
    return {}


def _node_has_lgrc9v3_identity_acceptance(
    node_record: Mapping[str, Any], *, checkpoint: GraphCheckpointArtifact
) -> bool:
    return bool(_lgrc9v3_identity_evidence_for_node(node_record, checkpoint=checkpoint))


def _is_int_like(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, str) and value.strip():
        return value.strip().lstrip("-").isdigit()
    return False


def _collapse_target_ids(checkpoint: GraphCheckpointArtifact) -> set[str]:
    target_ids: set[str] = set()
    for node_record in checkpoint.node_records:
        if not _node_is_collapsed_inactive(node_record):
            continue
        collapsed_sink_id = node_record.get("collapsed_sink_id")
        if _is_int_like(collapsed_sink_id):
            target_ids.add(str(int(collapsed_sink_id)))
    return target_ids


def _collapse_target_ids_from_node_record(node_record: Mapping[str, Any]) -> set[str]:
    collapsed_sink_id = node_record.get("collapsed_sink_id")
    if _is_int_like(collapsed_sink_id):
        return {str(int(collapsed_sink_id))}
    return set()


def _node_is_collapsed_inactive(node_record: Mapping[str, Any]) -> bool:
    return bool(node_record.get("collapse_flag")) and not bool(node_record.get("choice_flag"))


__all__ = [
    "render_graph_comparison_visual_bundle",
    "render_graph_run_visual_bundle",
]
