"""Visualization wrappers for replayed GRCL-9 lowering sessions."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/pygrc-matplotlib")

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
import networkx as nx

from pygrc.core import canonical_json_dumps, canonicalize_json_value
from pygrc.telemetry.grcl9_replay import GRCL9_REPLAY_ROOT, LEGACY_GROWTH_SOURCE_MODES
from pygrc.telemetry.io import build_telemetry_artifact_layout, load_telemetry_artifact_pack
from pygrc.telemetry.schema import GraphCheckpointArtifact
from pygrc.telemetry.io import TelemetryArtifactPack

from .graph_render import render_graph_run_visual_bundle
from .layout import build_graph_run_visualization_layout, build_run_visualization_layout
from .render import DEFAULT_GRC9_RUN_OBSERVABLES, render_run_visual_bundle


GRCL9_VISUALIZATION_VERSION = "grcl9_lowering_visualization_v1"
GRCL9_OVERLAY_FILENAME = "grcl9_lowering_overlay.png"
GRCL9_OVERLAY_SUMMARY_FILENAME = "grcl9_overlay_summary.json"
GRCL9_BOUNDARY_PANEL_FILENAME = "source_runtime_boundary.md"
GRCL9_PHASE_DIAGRAM_SUMMARY_JSON = "phase_diagram_summary.json"
GRCL9_PHASE_DIAGRAM_SUMMARY_MD = "phase_diagram_summary.md"
GRCL9_PHASE_DIAGRAM_VISUAL_INDEX_MD = "phase_diagram_visual_index.md"
_COLLAPSE_ADJACENT_EDGE_COLOR = "#d81b60"
_COLLAPSE_ADJACENT_TARGET_EDGE_COLOR = "#f9a825"
_COLLAPSE_ADJACENT_SELECTOR_IDS = frozenset(
    {
        "membrane_rupture_structural_probe",
        "fission_persistence_failed_candidate",
        "basin_merge_pressure_candidate",
        "support_loss_pressure_candidate",
        "saddle_pressure_structural_probe",
        "runtime_collapse_like_observed",
        "runtime_collapse_like_long_window",
    }
)


@dataclass(frozen=True)
class GRCL9VisualizationLaneResult:
    """Visualization artifacts for one replayed GRCL-9 lane."""

    fixture_name: str
    selector_status: str
    visualization_dir: str
    trajectory_path: str
    event_timeline_path: str
    graph_sequence_path: str
    graph_html_path: str
    grcl9_overlay_path: str
    grcl9_overlay_summary_path: str
    boundary_panel_path: str
    connected: bool
    bridge_edge_count: int
    motif_roles: tuple[str, ...]
    growth_parent_eligibility_mode: str
    growth_semantics_status: str
    evidence_status: str
    legacy_broad_growth_non_evidence: bool

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "fixture_name": self.fixture_name,
            "selector_status": self.selector_status,
            "visualization_dir": self.visualization_dir,
            "trajectory_path": self.trajectory_path,
            "event_timeline_path": self.event_timeline_path,
            "graph_sequence_path": self.graph_sequence_path,
            "graph_html_path": self.graph_html_path,
            "grcl9_overlay_path": self.grcl9_overlay_path,
            "grcl9_overlay_summary_path": self.grcl9_overlay_summary_path,
            "boundary_panel_path": self.boundary_panel_path,
            "connected": self.connected,
            "bridge_edge_count": self.bridge_edge_count,
            "motif_roles": list(self.motif_roles),
            "growth_parent_eligibility_mode": self.growth_parent_eligibility_mode,
            "growth_semantics_status": self.growth_semantics_status,
            "evidence_status": self.evidence_status,
            "legacy_broad_growth_non_evidence": self.legacy_broad_growth_non_evidence,
        }


@dataclass(frozen=True)
class GRCL9VisualizationSessionResult:
    """Visualization result for a replayed GRCL-9 lowering session."""

    session_id: str
    session_root: Path
    visualization_root: Path
    lanes: tuple[GRCL9VisualizationLaneResult, ...]
    visualization_manifest_path: Path
    index_path: Path

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "session_root": str(self.session_root),
            "visualization_root": str(self.visualization_root),
            "lane_count": len(self.lanes),
            "lanes": [lane.to_mapping() for lane in self.lanes],
            "visualization_manifest_path": str(self.visualization_manifest_path),
            "index_path": str(self.index_path),
        }


def render_grcl9_lowering_visual_session(
    *,
    session_root: str | Path = GRCL9_REPLAY_ROOT / "sessions" / "S0001",
    fixture_names: Sequence[str] | None = None,
    force_legacy_growth: bool = False,
) -> GRCL9VisualizationSessionResult:
    """Render behavior, graph, and GRCL-9 overlay visuals for one replay session."""

    root = Path(session_root)
    session_manifest_path = root / "session_manifest.json"
    if not session_manifest_path.exists():
        raise FileNotFoundError(f"missing GRCL-9 session manifest: {session_manifest_path}")
    session_manifest = _read_json(session_manifest_path)
    if _session_manifest_uses_legacy_growth(session_manifest) and not force_legacy_growth:
        raise ValueError(
            "GRCL-9 visualization refuses legacy broad-growth replay sessions. "
            "Use --force-legacy-growth only to render historical diagnostic "
            "artifacts; legacy visuals remain non-evidence."
        )
    lane_records = tuple(session_manifest.get("lanes", ()))
    selected = set(fixture_names or ())
    if selected:
        lane_records = tuple(
            lane for lane in lane_records if str(lane.get("fixture_name")) in selected
        )
    if not lane_records:
        raise ValueError("no GRCL-9 replay lanes selected for visualization")

    visualization_root = root / "visualizations"
    visualization_root.mkdir(parents=True, exist_ok=True)
    lane_results: list[GRCL9VisualizationLaneResult] = []
    for lane_record in lane_records:
        lane_results.append(
            _render_lane_visuals(
                lane_record=lane_record,
                visualization_root=visualization_root,
            )
        )

    result = GRCL9VisualizationSessionResult(
        session_id=str(session_manifest.get("session_id", root.name)),
        session_root=root,
        visualization_root=visualization_root,
        lanes=tuple(lane_results),
        visualization_manifest_path=visualization_root / "visualization_manifest.json",
        index_path=visualization_root / "index.md",
    )
    _write_json(result.visualization_manifest_path, result.to_mapping())
    _write_index(result.index_path, result)
    _write_phase_diagram_artifacts(root, result)
    return result


def _session_manifest_uses_legacy_growth(session_manifest: Mapping[str, Any]) -> bool:
    if str(session_manifest.get("source_mode", "")) in LEGACY_GROWTH_SOURCE_MODES:
        return True
    for lane in session_manifest.get("lanes", ()):
        if not isinstance(lane, Mapping):
            continue
        if bool(lane.get("legacy_broad_growth_non_evidence", False)):
            return True
    return False


def _render_lane_visuals(
    *,
    lane_record: Mapping[str, Any],
    visualization_root: Path,
) -> GRCL9VisualizationLaneResult:
    fixture_name = str(lane_record["fixture_name"])
    artifact_root = Path(str(lane_record["artifact_root"]))
    telemetry_layout = build_telemetry_artifact_layout(
        artifact_root.name,
        root_dir=artifact_root.parent,
    )
    pack = load_telemetry_artifact_pack(telemetry_layout)
    selector_report_path = Path(str(lane_record["selector_report_path"]))
    selector_report = _read_json(selector_report_path)
    run_summary = _read_json(artifact_root / "telemetry" / "run_summary.json")

    run_layout = build_run_visualization_layout(
        telemetry_layout,
        visualization_root=visualization_root,
    )
    graph_layout = build_graph_run_visualization_layout(
        telemetry_layout,
        visualization_root=visualization_root,
    )
    render_run_visual_bundle(
        pack,
        layout=run_layout,
        observables=DEFAULT_GRC9_RUN_OBSERVABLES,
    )
    render_graph_run_visual_bundle(pack, layout=graph_layout)

    initial_checkpoint = _initial_checkpoint(pack)
    final_checkpoint = _final_checkpoint(pack)
    overlay_summary = _grcl9_overlay_summary(
        source_checkpoint=initial_checkpoint,
        runtime_checkpoint=final_checkpoint,
        lane_record=lane_record,
        selector_report=selector_report,
        run_summary=run_summary,
    )
    overlay_path = graph_layout.run_dir / GRCL9_OVERLAY_FILENAME
    summary_path = graph_layout.run_dir / GRCL9_OVERLAY_SUMMARY_FILENAME
    boundary_path = graph_layout.run_dir / GRCL9_BOUNDARY_PANEL_FILENAME
    _render_grcl9_overlay(initial_checkpoint, overlay_summary, overlay_path)
    _write_json(summary_path, overlay_summary)
    _write_boundary_panel(boundary_path, overlay_summary)

    return GRCL9VisualizationLaneResult(
        fixture_name=fixture_name,
        selector_status=str(selector_report.get("status", "unknown")),
        visualization_dir=str(graph_layout.run_dir),
        trajectory_path=str(run_layout.trajectory_figure_path),
        event_timeline_path=str(run_layout.event_timeline_path),
        graph_sequence_path=str(graph_layout.sequence_figure_path),
        graph_html_path=str(graph_layout.final_html_path),
        grcl9_overlay_path=str(overlay_path),
        grcl9_overlay_summary_path=str(summary_path),
        boundary_panel_path=str(boundary_path),
        connected=bool(overlay_summary["connected"]),
        bridge_edge_count=int(overlay_summary["bridge_edge_count"]),
        motif_roles=tuple(overlay_summary["motif_roles"]),
        growth_parent_eligibility_mode=str(
            overlay_summary["growth_metadata"]["growth_parent_eligibility_mode"]
        ),
        growth_semantics_status=str(
            overlay_summary["growth_metadata"]["growth_semantics_status"]
        ),
        evidence_status=str(overlay_summary["growth_metadata"]["evidence_status"]),
        legacy_broad_growth_non_evidence=bool(
            overlay_summary["growth_metadata"]["legacy_broad_growth_non_evidence"]
        ),
    )


def _final_checkpoint(pack: TelemetryArtifactPack) -> GraphCheckpointArtifact:
    if not pack.graph_checkpoints:
        raise ValueError(
            "GRCL-9 lowering visualization requires saved graph checkpoints"
        )
    return tuple(
        sorted(
            pack.graph_checkpoints,
            key=lambda checkpoint: (
                checkpoint.step_index,
                checkpoint.time,
                checkpoint.checkpoint_label,
                checkpoint.checkpoint_id,
            ),
        )
    )[-1]


def _initial_checkpoint(pack: TelemetryArtifactPack) -> GraphCheckpointArtifact:
    if not pack.graph_checkpoints:
        raise ValueError(
            "GRCL-9 lowering visualization requires saved graph checkpoints"
        )
    return tuple(
        sorted(
            pack.graph_checkpoints,
            key=lambda checkpoint: (
                checkpoint.step_index,
                checkpoint.time,
                checkpoint.checkpoint_label,
                checkpoint.checkpoint_id,
            ),
        )
    )[0]


def _grcl9_overlay_summary(
    *,
    source_checkpoint: GraphCheckpointArtifact,
    runtime_checkpoint: GraphCheckpointArtifact,
    lane_record: Mapping[str, Any],
    selector_report: Mapping[str, Any],
    run_summary: Mapping[str, Any],
) -> Mapping[str, Any]:
    graph = _checkpoint_graph(source_checkpoint)
    node_roles = {
        str(node_record["node_id"]): _payload_string(
            node_record, "grcl9_motif_role", default="unlabeled_node"
        )
        for node_record in source_checkpoint.node_records
    }
    edge_roles = {
        str(edge_record["edge_id"]): _payload_string(
            edge_record, "grcl9_motif_role", default="unlabeled_edge"
        )
        for edge_record in source_checkpoint.edge_records
    }
    bridge_edge_ids = [
        int(edge_record["edge_id"])
        for edge_record in source_checkpoint.edge_records
        if _payload_string(edge_record, "grcl9_edge_kind", default="") == "bridge"
        or bool(edge_record.get("payload", {}).get("grcl9_bridge"))
    ]
    construct_kinds = sorted(
        {
            _payload_string(node_record, "grcl9_source_construct_kind", default="")
            for node_record in source_checkpoint.node_records
        }
        | {
            _payload_string(edge_record, "grcl9_source_construct_kind", default="")
            for edge_record in source_checkpoint.edge_records
        }
    )
    construct_kinds = [kind for kind in construct_kinds if kind]
    selector_results = tuple(selector_report.get("selector_results", ()))
    collapse_adjacent_visuals = _collapse_adjacent_visuals(
        node_roles=node_roles,
        selector_results=selector_results,
    )
    growth_metadata = _growth_visual_metadata(
        lane_record=lane_record,
        run_summary=run_summary,
    )
    return {
        "visualization_version": GRCL9_VISUALIZATION_VERSION,
        "fixture_name": str(lane_record.get("fixture_name", "")),
        "manifest_entry_id": str(lane_record.get("manifest_entry_id", "")),
        "run_id": str(lane_record.get("run_id", "")),
        "selector_status": str(selector_report.get("status", "unknown")),
        "source_intent": {
            "construct_kinds": construct_kinds,
            "expected_selector_ids": [
                str(result.get("selector_id", "")) for result in selector_results
            ],
            "claim_boundary": (
                "GRCL-9 source declares lowering preconditions and intent; "
                "runtime observation comes only from GRC9 telemetry."
            ),
        },
        "runtime_observation": {
            "step_index": runtime_checkpoint.step_index,
            "event_count_window": runtime_checkpoint.event_count_window,
            "event_counts_by_kind_window": dict(runtime_checkpoint.event_counts_by_kind_window),
            "selector_results": list(selector_results),
        },
        "connected": nx.is_connected(graph) if graph.number_of_nodes() > 0 else False,
        "component_count": nx.number_connected_components(graph) if graph.number_of_nodes() > 0 else 0,
        "node_count": source_checkpoint.node_count,
        "edge_count": source_checkpoint.edge_count,
        "bridge_edge_count": len(bridge_edge_ids),
        "bridge_edge_ids": bridge_edge_ids,
        "growth_metadata": growth_metadata,
        "collapse_adjacent_visuals": collapse_adjacent_visuals,
        "motif_roles": sorted(set(node_roles.values()) | set(edge_roles.values())),
        "node_roles": node_roles,
        "edge_roles": edge_roles,
    }


def _growth_visual_metadata(
    *,
    lane_record: Mapping[str, Any],
    run_summary: Mapping[str, Any],
) -> Mapping[str, Any]:
    grcl9 = _family_extension(run_summary, "grcl9")
    grc9 = _family_extension(run_summary, "grc9")
    growth_summary = grc9.get("growth_summary", {})
    growth_parent_mode = str(
        grcl9.get(
            "growth_parent_eligibility_mode",
            lane_record.get("growth_parent_eligibility_mode", "unknown"),
        )
    )
    growth_semantics = str(
        grcl9.get(
            "growth_semantics_status",
            lane_record.get("growth_semantics_status", "unknown"),
        )
    )
    legacy_flag = bool(
        grcl9.get(
            "legacy_broad_growth_non_evidence",
            lane_record.get("legacy_broad_growth_non_evidence", False),
        )
    )
    legacy_count = int(growth_summary.get("legacy_broad_growth_count", 0) or 0)
    front_count = int(growth_summary.get("front_capacity_growth_count", 0) or 0)
    growth_count = int(growth_summary.get("growth_count", 0) or 0)
    evidence_status = (
        "legacy_broad_growth_non_evidence"
        if legacy_flag or growth_parent_mode == "legacy_any_inactive_port" or legacy_count > 0
        else "corrected_front_capacity_evidence"
    )
    return {
        "growth_parent_eligibility_mode": growth_parent_mode,
        "growth_semantics_status": growth_semantics,
        "legacy_broad_growth_non_evidence": legacy_flag,
        "front_capacity_growth_count": front_count,
        "legacy_broad_growth_count": legacy_count,
        "growth_count": growth_count,
        "evidence_status": evidence_status,
        "claim_boundary": (
            "corrected front-capacity growth may support evidence claims"
            if evidence_status == "corrected_front_capacity_evidence"
            else "legacy broad growth is replay-only diagnostic non-evidence"
        ),
    }


def _family_extension(run_summary: Mapping[str, Any], family: str) -> Mapping[str, Any]:
    extensions = run_summary.get("family_extensions", {})
    if not isinstance(extensions, Mapping):
        return {}
    value = extensions.get(family, {})
    return value if isinstance(value, Mapping) else {}


def _render_grcl9_overlay(
    checkpoint: GraphCheckpointArtifact,
    overlay_summary: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    graph = _checkpoint_graph(checkpoint)
    if graph.number_of_nodes() == 0:
        raise ValueError("cannot render empty GRCL-9 checkpoint graph")
    positions = nx.spring_layout(graph, seed=19, iterations=160)
    node_records = {
        int(node_record["node_id"]): node_record for node_record in checkpoint.node_records
    }
    edge_records = {
        int(edge_record["edge_id"]): edge_record for edge_record in checkpoint.edge_records
    }
    bridge_edge_ids = set(int(edge_id) for edge_id in overlay_summary["bridge_edge_ids"])
    node_colors = [
        _role_color(_payload_string(node_records[node_id], "grcl9_motif_role", default=""))
        for node_id in graph.nodes()
    ]
    node_colors_by_id = {
        node_id: _role_color(_payload_string(node_records[node_id], "grcl9_motif_role", default=""))
        for node_id in graph.nodes()
    }
    node_labels = {
        node_id: _node_overlay_label(node_records[node_id])
        for node_id in graph.nodes()
    }
    collapse_adjacent_visuals = tuple(
        visual
        for visual in overlay_summary.get("collapse_adjacent_visuals", ())
        if isinstance(visual, Mapping)
    )
    collapse_sources = {
        int(visual["source_node_id"])
        for visual in collapse_adjacent_visuals
        if _is_int_like(visual.get("source_node_id"))
    }
    collapse_targets = {
        int(visual["target_node_id"])
        for visual in collapse_adjacent_visuals
        if _is_int_like(visual.get("target_node_id"))
    }
    normal_edges: list[tuple[int, int]] = []
    bridge_edges: list[tuple[int, int]] = []
    edge_labels: dict[tuple[int, int], str] = {}
    for source_id, target_id, data in graph.edges(data=True):
        edge_id = int(data["edge_id"])
        role = _payload_string(edge_records[edge_id], "grcl9_motif_role", default="")
        edge_labels[(source_id, target_id)] = _compact_role(role)
        if edge_id in bridge_edge_ids:
            bridge_edges.append((source_id, target_id))
        else:
            normal_edges.append((source_id, target_id))

    figure, axis = plt.subplots(figsize=(11, 8))
    nx.draw_networkx_edges(
        graph,
        positions,
        edgelist=normal_edges,
        ax=axis,
        edge_color="#6b7280",
        width=1.8,
        alpha=0.72,
    )
    if bridge_edges:
        nx.draw_networkx_edges(
            graph,
            positions,
            edgelist=bridge_edges,
            ax=axis,
            edge_color="#d62728",
            width=3.0,
            style="dashed",
            alpha=0.95,
        )
    _draw_collapse_adjacent_overlays(
        axis,
        positions=positions,
        collapse_adjacent_visuals=collapse_adjacent_visuals,
    )
    normal_node_ids = [
        node_id
        for node_id in graph.nodes()
        if node_id not in collapse_sources and node_id not in collapse_targets
    ]
    if normal_node_ids:
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=normal_node_ids,
            ax=axis,
            node_color=[node_colors_by_id[node_id] for node_id in normal_node_ids],
            edgecolors="#111827",
            linewidths=1.2,
            node_size=900,
        )
    target_node_ids = sorted(node_id for node_id in collapse_targets if node_id in graph)
    if target_node_ids:
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=target_node_ids,
            ax=axis,
            node_color=[node_colors_by_id[node_id] for node_id in target_node_ids],
            edgecolors=_COLLAPSE_ADJACENT_TARGET_EDGE_COLOR,
            linewidths=2.8,
            node_size=980,
        )
    source_node_ids = sorted(node_id for node_id in collapse_sources if node_id in graph)
    if source_node_ids:
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=source_node_ids,
            ax=axis,
            node_color=[node_colors_by_id[node_id] for node_id in source_node_ids],
            edgecolors=_COLLAPSE_ADJACENT_EDGE_COLOR,
            linewidths=3.2,
            node_size=980,
            alpha=0.38,
        )
    nx.draw_networkx_labels(
        graph,
        positions,
        labels=node_labels,
        ax=axis,
        font_size=7,
    )
    if len(edge_labels) <= 16:
        nx.draw_networkx_edge_labels(
            graph,
            positions,
            edge_labels=edge_labels,
            ax=axis,
            font_size=6,
            rotate=False,
        )
    axis.set_title(
        f"GRCL-9 lowering overlay: {overlay_summary['fixture_name']}\n"
        "source intent labels from lowering payloads; runtime observation from GRC9 checkpoints",
        fontsize=12,
    )
    axis.text(
        0.01,
        0.01,
        (
            f"connected={overlay_summary['connected']}  "
            f"bridge_edges={overlay_summary['bridge_edge_count']}  "
            f"collapse_adjacent={len(collapse_adjacent_visuals)}  "
            f"selector_status={overlay_summary['selector_status']}  "
            f"growth={overlay_summary['growth_metadata']['evidence_status']}"
        ),
        transform=axis.transAxes,
        fontsize=9,
        va="bottom",
        ha="left",
        bbox={"facecolor": "#ffffff", "edgecolor": "#d1d5db", "alpha": 0.9},
    )
    axis.set_axis_off()
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def _collapse_adjacent_visuals(
    *,
    node_roles: Mapping[str, str],
    selector_results: Sequence[Any],
) -> list[Mapping[str, Any]]:
    visuals_by_pair: dict[tuple[int, int], dict[str, Any]] = {}
    for raw_result in selector_results:
        if not isinstance(raw_result, Mapping):
            continue
        selector_id = str(raw_result.get("selector_id", ""))
        if selector_id not in _COLLAPSE_ADJACENT_SELECTOR_IDS:
            continue
        if not bool(raw_result.get("passed", False)):
            continue
        pair = _collapse_adjacent_pair(selector_id, node_roles)
        if pair is None:
            continue
        source_node_id, target_node_id = pair
        key = (source_node_id, target_node_id)
        existing = visuals_by_pair.get(key)
        if existing is None:
            existing = {
                "visual_kind": "collapse_adjacent_structural_probe",
                "source_node_id": source_node_id,
                "target_node_id": target_node_id,
                "source_role": node_roles.get(str(source_node_id), "unlabeled_node"),
                "target_role": node_roles.get(str(target_node_id), "unlabeled_node"),
                "selector_ids": [],
                "arrow_semantics": (
                    "source-declared structural pressure direction; "
                    "shared GRCV3 collapse visual grammar without runtime collapse semantics"
                ),
                "claim_boundary": (
                    "This marker is a GRCL-9 structural probe. It does not claim "
                    "a GRC9 collapse event or import GRCV3 choice/collapse semantics."
                ),
            }
            visuals_by_pair[key] = existing
        existing["selector_ids"].append(selector_id)
    visuals: list[Mapping[str, Any]] = []
    for visual in visuals_by_pair.values():
        visual["selector_ids"] = sorted(set(str(value) for value in visual["selector_ids"]))
        visuals.append(visual)
    return sorted(
        visuals,
        key=lambda visual: (
            int(visual["source_node_id"]),
            int(visual["target_node_id"]),
            tuple(visual["selector_ids"]),
        ),
    )


def _collapse_adjacent_pair(
    selector_id: str,
    node_roles: Mapping[str, str],
) -> tuple[int, int] | None:
    if selector_id in {
        "fission_persistence_failed_candidate",
        "basin_merge_pressure_candidate",
        "runtime_collapse_like_observed",
        "runtime_collapse_like_long_window",
    }:
        return _role_pair(node_roles, source_prefixes=("fission_sink_b",), target_prefixes=("fission_sink_a",))
    if selector_id == "support_loss_pressure_candidate":
        return _role_pair(
            node_roles,
            source_prefixes=("growth_support_2", "growth_support_1"),
            target_prefixes=("growth_parent",),
        )
    if selector_id == "saddle_pressure_structural_probe":
        return _role_pair(
            node_roles,
            source_prefixes=("candidate",),
            target_prefixes=("instability_cut_1", "neighbor_port_1"),
        )
    if selector_id == "membrane_rupture_structural_probe":
        return _role_pair(
            node_roles,
            source_prefixes=("candidate",),
            target_prefixes=("neighbor_port_1",),
        )
    return None


def _role_pair(
    node_roles: Mapping[str, str],
    *,
    source_prefixes: Sequence[str],
    target_prefixes: Sequence[str],
) -> tuple[int, int] | None:
    source_node_id = _first_node_with_role(node_roles, source_prefixes)
    target_node_id = _first_node_with_role(node_roles, target_prefixes)
    if source_node_id is None or target_node_id is None or source_node_id == target_node_id:
        return None
    return (source_node_id, target_node_id)


def _first_node_with_role(
    node_roles: Mapping[str, str],
    role_prefixes: Sequence[str],
) -> int | None:
    for role_prefix in role_prefixes:
        candidates = [
            int(node_id)
            for node_id, role in node_roles.items()
            if _is_int_like(node_id) and role.startswith(role_prefix)
        ]
        if candidates:
            return min(candidates)
    return None


def _draw_collapse_adjacent_overlays(
    axis: Any,
    *,
    positions: Mapping[int, Any],
    collapse_adjacent_visuals: Sequence[Mapping[str, Any]],
) -> None:
    edges: list[tuple[int, int]] = []
    for visual in collapse_adjacent_visuals:
        source_node_id = visual.get("source_node_id")
        target_node_id = visual.get("target_node_id")
        if not _is_int_like(source_node_id) or not _is_int_like(target_node_id):
            continue
        source_id = int(source_node_id)
        target_id = int(target_node_id)
        if source_id not in positions or target_id not in positions:
            continue
        edges.append((source_id, target_id))
    if not edges:
        return
    collapse_graph = nx.DiGraph()
    collapse_graph.add_edges_from(edges)
    nx.draw_networkx_edges(
        collapse_graph,
        positions,
        ax=axis,
        edge_color=_COLLAPSE_ADJACENT_EDGE_COLOR,
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


def _checkpoint_graph(checkpoint: GraphCheckpointArtifact) -> nx.Graph:
    graph = nx.Graph()
    for node_record in checkpoint.node_records:
        graph.add_node(int(node_record["node_id"]))
    for edge_record in checkpoint.edge_records:
        graph.add_edge(
            int(edge_record["source_node_id"]),
            int(edge_record["target_node_id"]),
            edge_id=int(edge_record["edge_id"]),
        )
    return graph


def _node_overlay_label(node_record: Mapping[str, Any]) -> str:
    role = _compact_role(_payload_string(node_record, "grcl9_motif_role", default="node"))
    return f"{node_record.get('node_id')}\n{role}"


def _payload_string(
    record: Mapping[str, Any],
    key: str,
    *,
    default: str,
) -> str:
    payload = record.get("payload", {})
    if isinstance(payload, Mapping):
        value = payload.get(key)
        if value is not None:
            return str(value)
    return default


def _is_int_like(value: Any) -> bool:
    try:
        int(value)
    except (TypeError, ValueError):
        return False
    return True


def _compact_role(role: str) -> str:
    return role.replace("_", "\n") if len(role) > 14 else role


def _role_color(role: str) -> str:
    if "candidate" in role:
        return "#f59e0b"
    if "neighbor" in role or "support" in role:
        return "#60a5fa"
    if "growth" in role:
        return "#34d399"
    if "fission" in role or "sink" in role:
        return "#a78bfa"
    if "expansion" in role:
        return "#f472b6"
    return "#cbd5e1"


def _write_boundary_panel(path: Path, overlay_summary: Mapping[str, Any]) -> None:
    source_intent = overlay_summary["source_intent"]
    runtime_observation = overlay_summary["runtime_observation"]
    growth_metadata = overlay_summary["growth_metadata"]
    collapse_adjacent_visuals = tuple(overlay_summary.get("collapse_adjacent_visuals", ()))
    lines = [
        f"# {overlay_summary['fixture_name']}",
        "",
        "## Source Intent",
        "",
        "GRCL-9 source declarations represented in the lowered checkpoint payloads:",
        "",
        "- Construct kinds: "
        + ", ".join(f"`{kind}`" for kind in source_intent["construct_kinds"]),
        "- Expected selectors: "
        + ", ".join(
            f"`{selector}`" for selector in source_intent["expected_selector_ids"]
        ),
        "- Boundary: source declarations are preconditions and intent labels, not runtime outcomes.",
        "",
        "## Runtime Observation",
        "",
        "GRC9 telemetry/checkpoint observations for the rendered lane:",
        "",
        f"- Selector status: `{overlay_summary['selector_status']}`",
        f"- Growth evidence status: `{growth_metadata['evidence_status']}`",
        f"- Growth parent eligibility: `{growth_metadata['growth_parent_eligibility_mode']}`",
        f"- Growth semantics status: `{growth_metadata['growth_semantics_status']}`",
        f"- Front-capacity growth count: `{growth_metadata['front_capacity_growth_count']}`",
        f"- Legacy broad-growth count: `{growth_metadata['legacy_broad_growth_count']}`",
        f"- Final checkpoint step: `{runtime_observation['step_index']}`",
        f"- Connected graph: `{overlay_summary['connected']}`",
        f"- Bridge edge count: `{overlay_summary['bridge_edge_count']}`",
        f"- Event window count: `{runtime_observation['event_count_window']}`",
        "- Event kinds in final window: "
        + ", ".join(
            f"`{key}={value}`"
            for key, value in sorted(
                runtime_observation["event_counts_by_kind_window"].items()
            )
        ),
        "",
        "## Visual Legend",
        "",
        "- Red dashed edges are explicit GRCL-9 bridge edges.",
        "- Node labels show node id and lowered motif role.",
        "- Behavior plots and graph snapshots are read from saved telemetry artifacts.",
        "- Corrected front-capacity lanes are evidence candidates; legacy broad-growth lanes are replay-only diagnostics.",
        "",
    ]
    if collapse_adjacent_visuals:
        lines.extend(
            [
                "## Collapse-Adjacent Structural Probe",
                "",
                (
                    "Transparent marked nodes and magenta dashed arrows reuse the "
                    "GRCV3 collapse visual grammar for directional readability. "
                    "For GRCL-9 these marks are structural-probe evidence, not runtime collapse."
                ),
                "",
            ]
        )
        for visual in collapse_adjacent_visuals:
            if not isinstance(visual, Mapping):
                continue
            selector_ids = ", ".join(
                f"`{selector_id}`" for selector_id in visual.get("selector_ids", ())
            )
            lines.append(
                f"- `{visual.get('source_node_id')}` ({visual.get('source_role')}) -> "
                f"`{visual.get('target_node_id')}` ({visual.get('target_role')}); "
                f"selectors: {selector_ids}"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_index(path: Path, result: GRCL9VisualizationSessionResult) -> None:
    lines = [
        f"# GRCL-9 Visualization Session {result.session_id}",
        "",
        f"- Visualization version: `{GRCL9_VISUALIZATION_VERSION}`",
        f"- Session root: `{result.session_root}`",
        f"- Visualization root: `{result.visualization_root}`",
        f"- Lanes: {len(result.lanes)}",
        "",
        "| Fixture | Selector | Evidence | Growth mode | Connected | Bridges | Overlay | Boundary |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for lane in result.lanes:
        lines.append(
            f"| `{lane.fixture_name}` | `{lane.selector_status}` | "
            f"`{lane.evidence_status}` | `{lane.growth_parent_eligibility_mode}` | "
            f"`{lane.connected}` | {lane.bridge_edge_count} | "
            f"[overlay]({Path(lane.grcl9_overlay_path).relative_to(result.visualization_root)}) | "
            f"[boundary]({Path(lane.boundary_panel_path).relative_to(result.visualization_root)}) |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_phase_diagram_artifacts(
    session_root: Path,
    result: GRCL9VisualizationSessionResult,
) -> None:
    phase_records = _phase_diagram_records(session_root, result)
    if not phase_records:
        return
    reports_root = session_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    visual_root = result.visualization_root
    summary = _phase_diagram_summary(result.session_id, session_root, phase_records)
    _write_json(reports_root / GRCL9_PHASE_DIAGRAM_SUMMARY_JSON, summary)
    _write_phase_diagram_markdown(
        reports_root / GRCL9_PHASE_DIAGRAM_SUMMARY_MD,
        summary,
    )
    _write_phase_visual_index(
        visual_root / GRCL9_PHASE_DIAGRAM_VISUAL_INDEX_MD,
        result,
        phase_records,
    )


def _phase_diagram_records(
    session_root: Path,
    result: GRCL9VisualizationSessionResult,
) -> tuple[Mapping[str, Any], ...]:
    records: list[Mapping[str, Any]] = []
    lane_by_fixture = {lane.fixture_name: lane for lane in result.lanes}
    for fixture_name, lane in sorted(lane_by_fixture.items()):
        prefix = "cell_full_capacity_phase_"
        if not fixture_name.startswith(prefix):
            continue
        suffix = fixture_name[len(prefix):]
        regime = None
        growth = None
        for candidate in ("balanced", "mild", "threshold", "deep"):
            marker = f"{candidate}_"
            if suffix.startswith(marker):
                regime = candidate
                growth = suffix[len(marker):]
                break
        if regime is None or growth is None:
            continue
        selector_path = session_root / "reports" / f"{fixture_name}_selector_report.json"
        if not selector_path.exists():
            continue
        report = _read_json(selector_path)
        selector_results = tuple(report.get("selector_results", ()))
        classification = _phase_classification(selector_results)
        event_counts = _phase_event_counts(selector_results)
        event_count_total = sum(int(value) for value in event_counts.values())
        records.append(
            {
                "fixture_name": fixture_name,
                "basin_regime": regime,
                "growth_regime": growth,
                "selector_status": str(report.get("status", lane.selector_status)),
                "classification": classification["classification"],
                "lost_source_sink_roles": classification["lost_source_sink_roles"],
                "target_selected_node_id": classification["target_selected_node_id"],
                "event_counts_by_kind": event_counts,
                "event_count_total": event_count_total,
                "module_size_observed": _phase_module_size(selector_results),
                "event_amplification_class": _event_amplification_class(event_counts),
                "graph_sequence_path": lane.graph_sequence_path,
                "event_timeline_path": lane.event_timeline_path,
                "overlay_path": lane.grcl9_overlay_path,
                "boundary_panel_path": lane.boundary_panel_path,
            }
        )
    order = {
        "balanced": 0,
        "mild": 1,
        "threshold": 2,
        "deep": 3,
        "no_growth": 0,
        "low_growth": 1,
        "nominal_growth": 2,
    }
    return tuple(
        sorted(
            records,
            key=lambda record: (
                order.get(str(record["basin_regime"]), 99),
                order.get(str(record["growth_regime"]), 99),
            ),
        )
    )


def _phase_classification(selector_results: Sequence[Any]) -> Mapping[str, Any]:
    for raw_result in selector_results:
        if not isinstance(raw_result, Mapping):
            continue
        selector_id = str(raw_result.get("selector_id", ""))
        if selector_id != "runtime_collapse_like_classification":
            continue
        observed = raw_result.get("observed_value", {})
        if not isinstance(observed, Mapping):
            break
        return {
            "classification": str(observed.get("classification", "unknown")),
            "lost_source_sink_roles": [
                str(role) for role in observed.get("lost_source_sink_roles", ())
            ],
            "target_selected_node_id": observed.get("target_selected_node_id"),
        }
    return {
        "classification": "unknown",
        "lost_source_sink_roles": [],
        "target_selected_node_id": None,
    }


def _phase_event_counts(selector_results: Sequence[Any]) -> dict[str, int]:
    by_selector: dict[str, int] = {}
    for raw_result in selector_results:
        if not isinstance(raw_result, Mapping):
            continue
        selector_id = str(raw_result.get("selector_id", ""))
        observed = raw_result.get("observed_value")
        if selector_id == "spark_column_proxy_count" and _is_int_like(observed):
            by_selector["spark"] = int(observed)
        elif selector_id == "expansion_module_size" and _is_int_like(observed):
            continue
        elif selector_id == "growth_count" and _is_int_like(observed):
            by_selector["growth"] = int(observed)
    return dict(sorted(by_selector.items()))


def _phase_module_size(selector_results: Sequence[Any]) -> int:
    for raw_result in selector_results:
        if not isinstance(raw_result, Mapping):
            continue
        if str(raw_result.get("selector_id", "")) != "expansion_module_size":
            continue
        observed = raw_result.get("observed_value")
        if _is_int_like(observed):
            return int(observed)
    return 0


def _event_amplification_class(event_counts: Mapping[str, int]) -> str:
    spark_count = int(event_counts.get("spark", 0))
    growth_count = int(event_counts.get("growth", 0))
    if spark_count >= 3 or growth_count >= 100:
        return "runaway"
    if growth_count > 0:
        return "active"
    return "quiet"


def _phase_diagram_summary(
    session_id: str,
    session_root: Path,
    records: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    matrix = {
        f"{record['basin_regime']}:{record['growth_regime']}": {
            "classification": record["classification"],
            "lost_source_sink_roles": list(record["lost_source_sink_roles"]),
            "event_amplification_class": record["event_amplification_class"],
            "event_counts_by_kind": dict(record["event_counts_by_kind"]),
        }
        for record in records
    }
    amplification_counts: dict[str, int] = {}
    classification_counts: dict[str, int] = {}
    for record in records:
        amplification = str(record["event_amplification_class"])
        amplification_counts[amplification] = amplification_counts.get(amplification, 0) + 1
        classification = str(record["classification"])
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
    return {
        "summary_version": "grcl9_phase_diagram_summary_v1",
        "session_id": session_id,
        "regime_axes": {
            "basin_regime": ["balanced", "mild", "threshold", "deep"],
            "growth_regime": ["no_growth", "low_growth", "nominal_growth"],
        },
        "lane_count": len(records),
        "classification_counts": dict(sorted(classification_counts.items())),
        "event_amplification_counts": dict(sorted(amplification_counts.items())),
        "reproducibility": {
            "working_directory": "repository root",
            "telemetry_replay_script": str(session_root / "replay.sh"),
            "telemetry_replay_command": _replay_command_text(session_root / "replay.sh"),
            "visualization_command": (
                "PYTHONPATH=src ./.venv/bin/python -m "
                f"pygrc.visualization.grcl9_lowering --session-root {session_root}"
            ),
        },
        "phase_matrix": matrix,
        "lanes": list(records),
        "interpretation": (
            "No-growth lanes are quiet but ambiguous; growth selects identity "
            "anchor loss direction. Threshold/deep regimes with growth produce "
            "collapse-like B-loss, while mild-low is the runaway amplification boundary."
        ),
    }


def _write_phase_diagram_markdown(path: Path, summary: Mapping[str, Any]) -> None:
    records = tuple(
        record for record in summary.get("lanes", ()) if isinstance(record, Mapping)
    )
    by_cell = {
        (str(record["basin_regime"]), str(record["growth_regime"])): record
        for record in records
    }
    growth_order = ("no_growth", "low_growth", "nominal_growth")
    lines = [
        f"# GRCL-9 Phase Diagram Summary {summary['session_id']}",
        "",
        f"- Summary version: `{summary['summary_version']}`",
        f"- Lane count: `{summary['lane_count']}`",
        f"- Classification counts: `{summary['classification_counts']}`",
        f"- Event amplification counts: `{summary['event_amplification_counts']}`",
        "",
        "## Reproducibility",
        "",
        "Run from the repository root:",
        "",
        "```bash",
        str(summary["reproducibility"]["telemetry_replay_command"]),
        str(summary["reproducibility"]["visualization_command"]),
        "```",
        "",
        "| Basin regime | No growth | Low growth | Nominal growth |",
        "|---|---|---|---|",
    ]
    for basin_regime in ("balanced", "mild", "threshold", "deep"):
        cells = []
        for growth_regime in growth_order:
            record = by_cell.get((basin_regime, growth_regime), {})
            cells.append(_phase_markdown_cell(record))
        lines.append(f"| `{basin_regime}` | " + " | ".join(cells) + " |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            str(summary["interpretation"]),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _replay_command_text(path: Path) -> str:
    if not path.exists():
        return ""
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        and not line.startswith("#!")
        and line.strip() != "set -euo pipefail"
    ]
    return " ".join(lines)


def _phase_markdown_cell(record: Mapping[str, Any]) -> str:
    if not record:
        return ""
    lost_roles = ",".join(str(role) for role in record.get("lost_source_sink_roles", ()))
    if not lost_roles:
        lost_roles = "none"
    return (
        f"`{record.get('classification')}`<br>"
        f"lost: `{lost_roles}`<br>"
        f"events: `{record.get('event_amplification_class')}`"
    )


def _write_phase_visual_index(
    path: Path,
    result: GRCL9VisualizationSessionResult,
    records: Sequence[Mapping[str, Any]],
) -> None:
    by_cell = {
        (str(record["basin_regime"]), str(record["growth_regime"])): record
        for record in records
    }
    lines = [
        f"# GRCL-9 Phase Diagram Visual Index {result.session_id}",
        "",
        "Each cell links to the lane graph sequence, event plot, overlay, and boundary panel.",
        "",
        "| Basin regime | No growth | Low growth | Nominal growth |",
        "|---|---|---|---|",
    ]
    for basin_regime in ("balanced", "mild", "threshold", "deep"):
        cells = [
            _phase_visual_cell(by_cell.get((basin_regime, growth_regime), {}), result.visualization_root)
            for growth_regime in ("no_growth", "low_growth", "nominal_growth")
        ]
        lines.append(f"| `{basin_regime}` | " + " | ".join(cells) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _phase_visual_cell(record: Mapping[str, Any], visualization_root: Path) -> str:
    if not record:
        return ""
    return (
        f"`{record.get('classification')}`<br>"
        f"[sequence]({_relative_link(record.get('graph_sequence_path'), visualization_root)}) "
        f"[events]({_relative_link(record.get('event_timeline_path'), visualization_root)}) "
        f"[overlay]({_relative_link(record.get('overlay_path'), visualization_root)}) "
        f"[boundary]({_relative_link(record.get('boundary_panel_path'), visualization_root)})"
    )


def _relative_link(path_value: Any, root: Path) -> str:
    path = Path(str(path_value))
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _read_json(path: Path) -> Mapping[str, Any]:
    import json

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError(f"expected JSON object at {path}")
    return raw


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        canonical_json_dumps(canonicalize_json_value(payload)) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--session-root",
        default=str(GRCL9_REPLAY_ROOT / "sessions" / "S0001"),
    )
    parser.add_argument(
        "--fixture",
        action="append",
        dest="fixtures",
        help="Fixture to render. May be passed multiple times.",
    )
    parser.add_argument(
        "--force-legacy-growth",
        action="store_true",
        help=(
            "Allow rendering quarantined legacy broad-growth sessions. Outputs "
            "remain diagnostic non-evidence."
        ),
    )
    args = parser.parse_args(argv)
    result = render_grcl9_lowering_visual_session(
        session_root=args.session_root,
        fixture_names=args.fixtures,
        force_legacy_growth=args.force_legacy_growth,
    )
    print(canonical_json_dumps(result.to_mapping()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "GRCL9_BOUNDARY_PANEL_FILENAME",
    "GRCL9_OVERLAY_FILENAME",
    "GRCL9_OVERLAY_SUMMARY_FILENAME",
    "GRCL9_PHASE_DIAGRAM_SUMMARY_JSON",
    "GRCL9_PHASE_DIAGRAM_SUMMARY_MD",
    "GRCL9_PHASE_DIAGRAM_VISUAL_INDEX_MD",
    "GRCL9_VISUALIZATION_VERSION",
    "GRCL9VisualizationLaneResult",
    "GRCL9VisualizationSessionResult",
    "render_grcl9_lowering_visual_session",
]
