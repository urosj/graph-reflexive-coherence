"""Visualization review for GRCL-9V3 lowered-source selector sessions."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/pygrc-matplotlib")

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
import networkx as nx

from pygrc.core import canonical_json_dumps, canonicalize_json_value
from pygrc.telemetry.grcl9v3_replay import GRCL9V3_REPLAY_ROOT
from pygrc.telemetry.io import build_telemetry_artifact_layout, load_telemetry_artifact_pack
from pygrc.telemetry.schema import GraphCheckpointArtifact
from pygrc.telemetry.io import TelemetryArtifactPack

from .graph_render import render_graph_run_visual_bundle
from .layout import build_graph_run_visualization_layout, build_run_visualization_layout
from .render import DEFAULT_GRC9V3_RUN_OBSERVABLES, render_run_visual_bundle


GRCL9V3_VISUALIZATION_VERSION = "grcl9v3_lowering_visualization_v1"
GRCL9V3_OVERLAY_FILENAME = "grcl9v3_lowering_overlay.png"
GRCL9V3_OVERLAY_SUMMARY_FILENAME = "grcl9v3_overlay_summary.json"
GRCL9V3_BOUNDARY_PANEL_FILENAME = "source_runtime_boundary.md"
GRCL9V3_VISUAL_STATUS = "rendered_supporting_only"


@dataclass(frozen=True)
class GRCL9V3VisualLaneRecord:
    """Visualization artifacts for one selector-backed GRCL-9V3 motif."""

    motif_id: str
    fixture_name: str
    source_session_id: str
    selector_session_id: str
    confidence_label: str
    confidence_score: int
    visual_status: str
    visualization_dir: str
    trajectory_path: str
    event_timeline_path: str
    graph_sequence_path: str
    dense_graph_sequence_path: str
    graph_animation_path: str
    graph_layout_path: str
    graph_html_path: str
    sparse_graph_overlay_path: str
    grcl9v3_overlay_path: str
    grcl9v3_overlay_summary_path: str
    boundary_panel_path: str
    selector_report_path: str
    selector_manifest_path: str
    source_fixture_path: str
    lowered_state_path: str
    telemetry_root: str
    connected: bool
    bridge_edge_count: int
    expected_region_cache_names: tuple[str, ...]
    motif_roles: tuple[str, ...]

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "motif_id": self.motif_id,
            "fixture_name": self.fixture_name,
            "source_session_id": self.source_session_id,
            "selector_session_id": self.selector_session_id,
            "confidence_label": self.confidence_label,
            "confidence_score": self.confidence_score,
            "visual_status": self.visual_status,
            "visualization_dir": self.visualization_dir,
            "trajectory_path": self.trajectory_path,
            "event_timeline_path": self.event_timeline_path,
            "graph_sequence_path": self.graph_sequence_path,
            "dense_graph_sequence_path": self.dense_graph_sequence_path,
            "graph_animation_path": self.graph_animation_path,
            "graph_layout_path": self.graph_layout_path,
            "graph_html_path": self.graph_html_path,
            "sparse_graph_overlay_path": self.sparse_graph_overlay_path,
            "grcl9v3_overlay_path": self.grcl9v3_overlay_path,
            "grcl9v3_overlay_summary_path": self.grcl9v3_overlay_summary_path,
            "boundary_panel_path": self.boundary_panel_path,
            "selector_report_path": self.selector_report_path,
            "selector_manifest_path": self.selector_manifest_path,
            "source_fixture_path": self.source_fixture_path,
            "lowered_state_path": self.lowered_state_path,
            "telemetry_root": self.telemetry_root,
            "connected": self.connected,
            "bridge_edge_count": self.bridge_edge_count,
            "expected_region_cache_names": list(self.expected_region_cache_names),
            "motif_roles": list(self.motif_roles),
        }


@dataclass(frozen=True)
class GRCL9V3SkippedVisualRecord:
    """Selector validation record intentionally not promoted to visuals."""

    fixture_name: str
    confidence_label: str
    reason: str
    telemetry_root: str

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "fixture_name": self.fixture_name,
            "confidence_label": self.confidence_label,
            "reason": self.reason,
            "telemetry_root": self.telemetry_root,
        }


@dataclass(frozen=True)
class GRCL9V3VisualReviewSession:
    """Visualization review session over GRCL-9V3 selector records."""

    session_id: str
    selector_session_id: str
    source_session_ids: tuple[str, ...]
    session_root: Path
    visualization_root: Path
    records: tuple[GRCL9V3VisualLaneRecord, ...]
    skipped_records: tuple[GRCL9V3SkippedVisualRecord, ...]
    visual_index_path: Path
    report_path: Path
    summary_path: Path
    session_manifest_path: Path

    def to_mapping(self) -> Mapping[str, Any]:
        labels = Counter(record.confidence_label for record in self.records)
        return {
            "session_id": self.session_id,
            "selector_session_id": self.selector_session_id,
            "source_session_ids": list(self.source_session_ids),
            "visualization_version": GRCL9V3_VISUALIZATION_VERSION,
            "record_count": len(self.records),
            "skipped_count": len(self.skipped_records),
            "strong_candidate_count": labels.get("strong_candidate", 0),
            "candidate_count": labels.get("candidate", 0),
            "ambiguous_count": labels.get("ambiguous", 0),
            "session_root": str(self.session_root),
            "visualization_root": str(self.visualization_root),
            "records": [record.to_mapping() for record in self.records],
            "skipped_records": [record.to_mapping() for record in self.skipped_records],
            "visual_index_path": str(self.visual_index_path),
            "report_path": str(self.report_path),
            "summary_path": str(self.summary_path),
            "session_manifest_path": str(self.session_manifest_path),
            "visual_claim_boundary": (
                "Visuals are supporting evidence only; selector telemetry remains primary."
            ),
            "no_visual_only_promotion": True,
        }


def render_grcl9v3_lowering_visual_review(
    *,
    session_id: str = "S0003",
    selector_session_id: str = "S0002",
    output_root: str | Path = GRCL9V3_REPLAY_ROOT,
    render_visuals: bool = True,
) -> GRCL9V3VisualReviewSession:
    """Render visual review artifacts for selector-backed GRCL-9V3 motifs."""

    _validate_session_id(session_id)
    _validate_session_id(selector_session_id)
    root = Path(output_root)
    selector_root = root / "sessions" / selector_session_id
    selector_manifest_path = selector_root / "selector_manifest.json"
    selector_report_path = selector_root / "reports" / "selector_validation_report.json"
    if not selector_manifest_path.exists():
        raise FileNotFoundError(f"missing selector manifest: {selector_manifest_path}")
    if not selector_report_path.exists():
        raise FileNotFoundError(f"missing selector report: {selector_report_path}")

    selector_manifest = _read_json(selector_manifest_path)
    selector_report = _read_json(selector_report_path)
    validations = tuple(selector_report.get("validations", ()))
    validation_by_lane = {
        str(validation.get("lane_name", validation.get("fixture_name", ""))): validation
        for validation in validations
        if isinstance(validation, Mapping)
    }
    motifs = tuple(
        motif for motif in selector_manifest.get("motifs", ()) if isinstance(motif, Mapping)
    )

    session_root = root / "sessions" / session_id
    visualization_root = session_root / "visualizations"
    reports_root = session_root / "reports"
    for path in (visualization_root, reports_root):
        path.mkdir(parents=True, exist_ok=True)

    records: list[GRCL9V3VisualLaneRecord] = []
    skipped: list[GRCL9V3SkippedVisualRecord] = []
    motif_lanes = {str(motif.get("lane", motif.get("fixture_name", ""))) for motif in motifs}
    for validation in validations:
        if not isinstance(validation, Mapping):
            continue
        lane_name = str(validation.get("lane_name", validation.get("fixture_name", "")))
        if lane_name in motif_lanes:
            continue
        skipped.append(
            GRCL9V3SkippedVisualRecord(
                fixture_name=str(validation.get("fixture_name", lane_name)),
                confidence_label=str(validation.get("confidence_label", "unknown")),
                reason="no_selector_backed_motif",
                telemetry_root=str(validation.get("telemetry_root", "")),
            )
        )

    for motif in motifs:
        lane_name = str(motif.get("lane", motif.get("fixture_name", "")))
        validation = validation_by_lane.get(lane_name, motif)
        if render_visuals:
            records.append(
                _render_visual_record(
                    motif=motif,
                    validation=validation,
                    selector_session_id=selector_session_id,
                    selector_manifest_path=selector_manifest_path,
                    selector_report_path=selector_report_path,
                    visualization_root=visualization_root,
                )
            )
        else:
            records.append(
                _placeholder_visual_record(
                    motif=motif,
                    validation=validation,
                    selector_session_id=selector_session_id,
                    selector_manifest_path=selector_manifest_path,
                    selector_report_path=selector_report_path,
                    visualization_root=visualization_root,
                )
            )

    session = GRCL9V3VisualReviewSession(
        session_id=session_id,
        selector_session_id=selector_session_id,
        source_session_ids=tuple(str(item) for item in selector_report.get("source_session_ids", ())),
        session_root=session_root,
        visualization_root=visualization_root,
        records=tuple(records),
        skipped_records=tuple(skipped),
        visual_index_path=session_root / "visual_index.json",
        report_path=reports_root / "visual_review_report.json",
        summary_path=reports_root / "visual_review_summary.md",
        session_manifest_path=session_root / "session_manifest.json",
    )
    _write_json(session.visual_index_path, _visual_index(session))
    _write_json(session.report_path, session.to_mapping())
    _write_summary_markdown(session.summary_path, session)
    _write_json(session.session_manifest_path, _session_manifest(session, root))
    _write_readme(session_root, session)
    _write_experimental_log(root / "ExperimentalLog.md", session)
    return session


def _render_visual_record(
    *,
    motif: Mapping[str, Any],
    validation: Mapping[str, Any],
    selector_session_id: str,
    selector_manifest_path: Path,
    selector_report_path: Path,
    visualization_root: Path,
) -> GRCL9V3VisualLaneRecord:
    fixture_name = str(motif.get("fixture_name", validation.get("fixture_name", "")))
    telemetry_root = Path(str(motif.get("telemetry_root", validation.get("telemetry_root", ""))))
    artifact_root = telemetry_root.parent
    telemetry_layout = build_telemetry_artifact_layout(
        artifact_root.name,
        root_dir=artifact_root.parent,
    )
    pack = load_telemetry_artifact_pack(telemetry_layout)
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
        observables=DEFAULT_GRC9V3_RUN_OBSERVABLES,
    )
    render_graph_run_visual_bundle(pack, layout=graph_layout)

    initial_checkpoint = _initial_checkpoint(pack)
    final_checkpoint = _final_checkpoint(pack)
    overlay_summary = _grcl9v3_overlay_summary(
        source_checkpoint=initial_checkpoint,
        runtime_checkpoint=final_checkpoint,
        pack=pack,
        motif=motif,
        validation=validation,
        selector_report_path=selector_report_path,
    )
    overlay_path = graph_layout.run_dir / GRCL9V3_OVERLAY_FILENAME
    summary_path = graph_layout.run_dir / GRCL9V3_OVERLAY_SUMMARY_FILENAME
    boundary_path = graph_layout.run_dir / GRCL9V3_BOUNDARY_PANEL_FILENAME
    _render_grcl9v3_overlay(final_checkpoint, overlay_summary, overlay_path)
    _write_json(summary_path, overlay_summary)
    _write_boundary_panel(boundary_path, overlay_summary)

    return GRCL9V3VisualLaneRecord(
        motif_id=str(motif["motif_id"]),
        fixture_name=fixture_name,
        source_session_id=str((motif.get("session_ids") or [""])[0]),
        selector_session_id=selector_session_id,
        confidence_label=str(motif.get("confidence_label", validation.get("confidence_label", ""))),
        confidence_score=int(motif.get("confidence_score", validation.get("confidence_score", 0))),
        visual_status=GRCL9V3_VISUAL_STATUS,
        visualization_dir=str(graph_layout.run_dir),
        trajectory_path=str(run_layout.trajectory_figure_path),
        event_timeline_path=str(run_layout.event_timeline_path),
        graph_sequence_path=str(graph_layout.sequence_figure_path),
        dense_graph_sequence_path=str(graph_layout.sequence_figure_path),
        graph_animation_path=str(graph_layout.animation_path),
        graph_layout_path=str(graph_layout.layout_json_path),
        graph_html_path=str(graph_layout.final_html_path),
        sparse_graph_overlay_path=str(overlay_path),
        grcl9v3_overlay_path=str(overlay_path),
        grcl9v3_overlay_summary_path=str(summary_path),
        boundary_panel_path=str(boundary_path),
        selector_report_path=str(selector_report_path),
        selector_manifest_path=str(selector_manifest_path),
        source_fixture_path=str(motif.get("source_fixture_path", validation.get("source_fixture_path", ""))),
        lowered_state_path=str(motif.get("lowered_state_path", validation.get("lowered_state_path", ""))),
        telemetry_root=str(telemetry_root),
        connected=bool(overlay_summary["connected"]),
        bridge_edge_count=int(overlay_summary["bridge_edge_count"]),
        expected_region_cache_names=tuple(overlay_summary["expected_region_cache_names"]),
        motif_roles=tuple(overlay_summary["motif_roles"]),
    )


def _placeholder_visual_record(
    *,
    motif: Mapping[str, Any],
    validation: Mapping[str, Any],
    selector_session_id: str,
    selector_manifest_path: Path,
    selector_report_path: Path,
    visualization_root: Path,
) -> GRCL9V3VisualLaneRecord:
    fixture_name = str(motif.get("fixture_name", validation.get("fixture_name", "")))
    placeholder_dir = visualization_root / fixture_name
    return GRCL9V3VisualLaneRecord(
        motif_id=str(motif["motif_id"]),
        fixture_name=fixture_name,
        source_session_id=str((motif.get("session_ids") or [""])[0]),
        selector_session_id=selector_session_id,
        confidence_label=str(motif.get("confidence_label", validation.get("confidence_label", ""))),
        confidence_score=int(motif.get("confidence_score", validation.get("confidence_score", 0))),
        visual_status="not_rendered",
        visualization_dir=str(placeholder_dir),
        trajectory_path="",
        event_timeline_path="",
        graph_sequence_path="",
        dense_graph_sequence_path="",
        graph_animation_path="",
        graph_layout_path="",
        graph_html_path="",
        sparse_graph_overlay_path="",
        grcl9v3_overlay_path="",
        grcl9v3_overlay_summary_path="",
        boundary_panel_path="",
        selector_report_path=str(selector_report_path),
        selector_manifest_path=str(selector_manifest_path),
        source_fixture_path=str(motif.get("source_fixture_path", validation.get("source_fixture_path", ""))),
        lowered_state_path=str(motif.get("lowered_state_path", validation.get("lowered_state_path", ""))),
        telemetry_root=str(motif.get("telemetry_root", validation.get("telemetry_root", ""))),
        connected=False,
        bridge_edge_count=0,
        expected_region_cache_names=(),
        motif_roles=(),
    )


def _grcl9v3_overlay_summary(
    *,
    source_checkpoint: GraphCheckpointArtifact,
    runtime_checkpoint: GraphCheckpointArtifact,
    pack: TelemetryArtifactPack,
    motif: Mapping[str, Any],
    validation: Mapping[str, Any],
    selector_report_path: Path,
) -> Mapping[str, Any]:
    graph = _checkpoint_graph(runtime_checkpoint)
    source_node_ids = {int(node_record["node_id"]) for node_record in source_checkpoint.node_records}
    source_edge_ids = {int(edge_record["edge_id"]) for edge_record in source_checkpoint.edge_records}
    node_roles = {
        str(node_record["node_id"]): _payload_string(
            node_record, "grcl9v3_motif_role", default="unlabeled_node"
        )
        for node_record in runtime_checkpoint.node_records
    }
    edge_roles = {
        str(edge_record["edge_id"]): _payload_string(
            edge_record, "grcl9v3_motif_role", default="unlabeled_edge"
        )
        for edge_record in runtime_checkpoint.edge_records
    }
    bridge_edge_ids = [
        int(edge_record["edge_id"])
        for edge_record in runtime_checkpoint.edge_records
        if _payload_string(edge_record, "grcl9v3_edge_kind", default="") == "bridge"
        or bool(edge_record.get("payload", {}).get("grcl9v3_bridge"))
    ]
    construct_kinds = sorted(
        {
            _payload_string_any(
                node_record,
                ("grcl9v3_source_construct_kind", "grcl9v3_construct_kind"),
                default="",
            )
            for node_record in runtime_checkpoint.node_records
        }
        | {
            _payload_string_any(
                edge_record,
                ("grcl9v3_source_construct_kind", "grcl9v3_construct_kind"),
                default="",
            )
            for edge_record in runtime_checkpoint.edge_records
        }
    )
    construct_kinds = [kind for kind in construct_kinds if kind]
    expected_caches = _expected_region_caches(pack, runtime_checkpoint)
    selector_results = tuple(validation.get("selector_results", ()))
    passed_selector_ids = tuple(
        str(result.get("selector_id", ""))
        for result in selector_results
        if isinstance(result, Mapping) and bool(result.get("passed", False))
    )
    missing_selector_ids = tuple(
        str(result.get("selector_id", ""))
        for result in selector_results
        if isinstance(result, Mapping) and not bool(result.get("passed", False))
    )
    missing_surface_selector_ids = tuple(
        str(result.get("selector_id", ""))
        for result in selector_results
        if isinstance(result, Mapping)
        and str(result.get("failure_kind", "")) == "missing_surface"
    )
    runtime_node_ids = {int(node_record["node_id"]) for node_record in runtime_checkpoint.node_records}
    runtime_edge_ids = {int(edge_record["edge_id"]) for edge_record in runtime_checkpoint.edge_records}
    return {
        "visualization_version": GRCL9V3_VISUALIZATION_VERSION,
        "fixture_name": str(motif.get("fixture_name", validation.get("fixture_name", ""))),
        "motif_id": str(motif.get("motif_id", "")),
        "manifest_entry_id": str(motif.get("manifest_entry_id", validation.get("manifest_entry_id", ""))),
        "run_id": str(motif.get("run_id", validation.get("run_id", ""))),
        "selector_confidence_label": str(motif.get("confidence_label", validation.get("confidence_label", ""))),
        "selector_confidence_score": int(motif.get("confidence_score", validation.get("confidence_score", 0))),
        "selector_report_path": str(selector_report_path),
        "source_fixture_path": str(motif.get("source_fixture_path", validation.get("source_fixture_path", ""))),
        "lowered_state_path": str(motif.get("lowered_state_path", validation.get("lowered_state_path", ""))),
        "telemetry_root": str(motif.get("telemetry_root", validation.get("telemetry_root", ""))),
        "visual_status": GRCL9V3_VISUAL_STATUS,
        "visual_claim_boundary": (
            "Supporting evidence only; selector telemetry is primary."
        ),
        "no_visual_only_promotion": True,
        "deterministic_layout": {
            "dense_graph_layout_policy": "shared union_static_spring",
            "dense_graph_layout_seed": 17,
            "sparse_overlay_layout_policy": "spring_layout_or_large_graph_grid",
            "sparse_overlay_layout_seed": 29,
            "node_ordering": "sorted checkpoint node ids",
        },
        "graph_surface_modes": {
            "dense": {
                "description": "full checkpoint-backed graph sequence, animation, layout JSON, and final HTML",
                "source": "Phase T-GRC9V3 graph checkpoints",
            },
            "sparse": {
                "description": "GRCL-9V3 source/runtime boundary overlay with motif-role labels",
                "source": "same checkpoints compressed by lowered source roles",
            },
        },
        "selector_ids": list(validation.get("expanded_selector_ids", ())),
        "passed_selector_ids": list(passed_selector_ids),
        "missing_selector_ids": list(missing_selector_ids),
        "missing_surface_selector_ids": list(missing_surface_selector_ids),
        "source_intent": {
            "construct_kinds": construct_kinds,
            "expected_selector_ids": [
                str(selector_id)
                for selector_id in motif.get(
                    "source_expected_selector_ids",
                    validation.get("source_expected_selector_ids", ()),
                )
            ],
            "claim_boundary": (
                "GRCL-9V3 source declares Morse/phenomenology preconditions and "
                "lowering intent; runtime observation comes from GRC9V3 telemetry."
            ),
        },
        "runtime_observation": {
            "step_index": runtime_checkpoint.step_index,
            "event_count_window": runtime_checkpoint.event_count_window,
            "event_counts_by_kind_window": dict(runtime_checkpoint.event_counts_by_kind_window),
            "run_event_counts_by_kind": dict(pack.run_summary.event_counts_by_kind),
            "selector_results": [canonicalize_json_value(result) for result in selector_results],
            "missing_surface_selector_ids": list(missing_surface_selector_ids),
        },
        "expected_region_caches": expected_caches,
        "expected_region_cache_names": sorted(expected_caches),
        "source_runtime_visual_distinction": {
            "source_node_ids": sorted(source_node_ids & runtime_node_ids),
            "runtime_added_node_ids": sorted(runtime_node_ids - source_node_ids),
            "source_edge_ids": sorted(source_edge_ids & runtime_edge_ids),
            "runtime_added_edge_ids": sorted(runtime_edge_ids - source_edge_ids),
            "visual_rule": (
                "source-derived nodes use dark borders; runtime-added nodes use red borders and white fill"
            ),
        },
        "connected": nx.is_connected(graph) if graph.number_of_nodes() > 0 else False,
        "component_count": nx.number_connected_components(graph) if graph.number_of_nodes() > 0 else 0,
        "node_count": runtime_checkpoint.node_count,
        "edge_count": runtime_checkpoint.edge_count,
        "bridge_edge_count": len(bridge_edge_ids),
        "bridge_edge_ids": bridge_edge_ids,
        "motif_roles": sorted(set(node_roles.values()) | set(edge_roles.values())),
        "node_roles": node_roles,
        "edge_roles": edge_roles,
    }


def _expected_region_caches(
    pack: TelemetryArtifactPack,
    runtime_checkpoint: GraphCheckpointArtifact,
) -> Mapping[str, Any]:
    checkpoint_ext = runtime_checkpoint.family_extensions.get("grcl9v3", {})
    if isinstance(checkpoint_ext, Mapping) and isinstance(
        checkpoint_ext.get("expected_region_caches"), Mapping
    ):
        return canonicalize_json_value(dict(checkpoint_ext["expected_region_caches"]))
    summary_ext = pack.run_summary.family_extensions.get("grcl9v3", {})
    if isinstance(summary_ext, Mapping) and isinstance(
        summary_ext.get("expected_region_caches"), Mapping
    ):
        return canonicalize_json_value(dict(summary_ext["expected_region_caches"]))
    return {}


def _render_grcl9v3_overlay(
    checkpoint: GraphCheckpointArtifact,
    overlay_summary: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    graph = _checkpoint_graph(checkpoint)
    if graph.number_of_nodes() == 0:
        raise ValueError("cannot render empty GRCL-9V3 checkpoint graph")
    positions = _overlay_layout(graph)
    node_records = {
        int(node_record["node_id"]): node_record for node_record in checkpoint.node_records
    }
    edge_records = {
        int(edge_record["edge_id"]): edge_record for edge_record in checkpoint.edge_records
    }
    bridge_edge_ids = set(int(edge_id) for edge_id in overlay_summary["bridge_edge_ids"])
    source_node_ids = set(
        int(node_id)
        for node_id in overlay_summary["source_runtime_visual_distinction"]["source_node_ids"]
    )
    runtime_added_node_ids = set(
        int(node_id)
        for node_id in overlay_summary["source_runtime_visual_distinction"]["runtime_added_node_ids"]
    )
    node_colors_by_id = {
        node_id: _role_color(_payload_string(node_records[node_id], "grcl9v3_motif_role", default=""))
        for node_id in graph.nodes()
    }
    node_labels = {
        node_id: _node_overlay_label(node_records[node_id])
        for node_id in graph.nodes()
    }
    normal_edges: list[tuple[int, int]] = []
    bridge_edges: list[tuple[int, int]] = []
    edge_labels: dict[tuple[int, int], str] = {}
    for source_id, target_id, data in graph.edges(data=True):
        edge_id = int(data["edge_id"])
        role = _payload_string(edge_records[edge_id], "grcl9v3_motif_role", default="")
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
    source_nodes = sorted(node_id for node_id in graph.nodes() if node_id in source_node_ids)
    if source_nodes:
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=source_nodes,
            ax=axis,
            node_color=[node_colors_by_id[node_id] for node_id in source_nodes],
            edgecolors="#111827",
            linewidths=1.2,
            node_size=900,
        )
    runtime_nodes = sorted(node_id for node_id in graph.nodes() if node_id in runtime_added_node_ids)
    if runtime_nodes:
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=runtime_nodes,
            ax=axis,
            node_color="#ffffff",
            edgecolors="#ef4444",
            linewidths=2.6,
            node_size=980,
        )
    unclassified_nodes = sorted(
        node_id
        for node_id in graph.nodes()
        if node_id not in source_node_ids and node_id not in runtime_added_node_ids
    )
    if unclassified_nodes:
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=unclassified_nodes,
            ax=axis,
            node_color=[node_colors_by_id[node_id] for node_id in unclassified_nodes],
            edgecolors="#64748b",
            linewidths=1.2,
            node_size=850,
        )
    nx.draw_networkx_labels(graph, positions, labels=node_labels, ax=axis, font_size=7)
    if len(edge_labels) <= 18:
        nx.draw_networkx_edge_labels(
            graph,
            positions,
            edge_labels=edge_labels,
            ax=axis,
            font_size=6,
            rotate=False,
        )
    axis.set_title(
        f"GRCL-9V3 lowering overlay: {overlay_summary['fixture_name']}\n"
        "source labels from lowering payloads; runtime evidence from selector-backed telemetry",
        fontsize=12,
    )
    axis.text(
        0.01,
        0.01,
        (
            f"connected={overlay_summary['connected']}  "
            f"bridge_edges={overlay_summary['bridge_edge_count']}  "
            f"runtime_added_nodes={len(runtime_added_node_ids)}  "
            f"confidence={overlay_summary['selector_confidence_label']}"
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


def _checkpoint_graph(checkpoint: GraphCheckpointArtifact) -> nx.Graph:
    graph = nx.Graph()
    for node_record in sorted(checkpoint.node_records, key=lambda record: int(record["node_id"])):
        graph.add_node(int(node_record["node_id"]))
    for edge_record in sorted(checkpoint.edge_records, key=lambda record: int(record["edge_id"])):
        graph.add_edge(
            int(edge_record["source_node_id"]),
            int(edge_record["target_node_id"]),
            edge_id=int(edge_record["edge_id"]),
        )
    return graph


def _overlay_layout(graph: nx.Graph) -> Mapping[int, tuple[float, float]]:
    if graph.number_of_nodes() >= 500:
        return _large_graph_grid_layout(sorted(int(node_id) for node_id in graph.nodes()))
    try:
        return nx.spring_layout(graph, seed=29, iterations=160, method="force")
    except TypeError:
        return nx.spring_layout(graph, seed=29, iterations=160)


def _large_graph_grid_layout(node_ids: Sequence[int]) -> Mapping[int, tuple[float, float]]:
    columns = max(1, int(math.ceil(math.sqrt(len(node_ids)))))
    positions: dict[int, tuple[float, float]] = {}
    for index, node_id in enumerate(node_ids):
        row, column = divmod(index, columns)
        positions[int(node_id)] = (float(column), float(-row))
    return _normalize_overlay_positions(positions)


def _normalize_overlay_positions(
    positions: Mapping[int, tuple[float, float]],
) -> Mapping[int, tuple[float, float]]:
    xs = [position[0] for position in positions.values()]
    ys = [position[1] for position in positions.values()]
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    span = max(max_x - min_x, max_y - min_y, 1e-9)
    center_x = 0.5 * (min_x + max_x)
    center_y = 0.5 * (min_y + max_y)
    return {
        int(node_id): (
            float((x_value - center_x) / span * 2.0),
            float((y_value - center_y) / span * 2.0),
        )
        for node_id, (x_value, y_value) in positions.items()
    }


def _node_overlay_label(node_record: Mapping[str, Any]) -> str:
    role = _compact_role(_payload_string(node_record, "grcl9v3_motif_role", default="node"))
    return f"{node_record.get('node_id')}\n{role}"


def _payload_string(record: Mapping[str, Any], key: str, *, default: str) -> str:
    payload = record.get("payload", {})
    if isinstance(payload, Mapping):
        value = payload.get(key)
        if value is not None:
            return str(value)
    return default


def _payload_string_any(
    record: Mapping[str, Any],
    keys: Sequence[str],
    *,
    default: str,
) -> str:
    payload = record.get("payload", {})
    if isinstance(payload, Mapping):
        for key in keys:
            value = payload.get(key)
            if value is not None:
                return str(value)
    return default


def _compact_role(role: str) -> str:
    return role.replace("_", "\n") if len(role) > 14 else role


def _role_color(role: str) -> str:
    if "spark" in role or "candidate" in role:
        return "#f59e0b"
    if "tensor" in role or "hessian" in role:
        return "#22c55e"
    if "choice" in role or "collapse" in role:
        return "#38bdf8"
    if "growth" in role:
        return "#34d399"
    if "fission" in role or "sink" in role or "appendix" in role:
        return "#a78bfa"
    if "expansion" in role:
        return "#f472b6"
    if "transport" in role:
        return "#fb7185"
    return "#cbd5e1"


def _final_checkpoint(pack: TelemetryArtifactPack) -> GraphCheckpointArtifact:
    if not pack.graph_checkpoints:
        raise ValueError("GRCL-9V3 visualization requires saved graph checkpoints")
    return _sorted_checkpoints(pack)[-1]


def _initial_checkpoint(pack: TelemetryArtifactPack) -> GraphCheckpointArtifact:
    if not pack.graph_checkpoints:
        raise ValueError("GRCL-9V3 visualization requires saved graph checkpoints")
    return _sorted_checkpoints(pack)[0]


def _sorted_checkpoints(pack: TelemetryArtifactPack) -> tuple[GraphCheckpointArtifact, ...]:
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
    )


def _write_boundary_panel(path: Path, overlay_summary: Mapping[str, Any]) -> None:
    source_intent = overlay_summary["source_intent"]
    runtime_observation = overlay_summary["runtime_observation"]
    lines = [
        f"# {overlay_summary['fixture_name']}",
        "",
        "## Source Intent",
        "",
        "GRCL-9V3 source declarations represented in the lowered checkpoint payloads:",
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
        "GRC9V3 telemetry/checkpoint observations for the rendered lane:",
        "",
        f"- Selector confidence: `{overlay_summary['selector_confidence_label']}`",
        f"- Selector score: `{overlay_summary['selector_confidence_score']}`",
        f"- Final checkpoint step: `{runtime_observation['step_index']}`",
        f"- Connected graph: `{overlay_summary['connected']}`",
        f"- Bridge edge count: `{overlay_summary['bridge_edge_count']}`",
        "- Run event counts: "
        + ", ".join(
            f"`{key}={value}`"
            for key, value in sorted(runtime_observation["run_event_counts_by_kind"].items())
        ),
        "",
        "## Visual Boundary",
        "",
        "These visuals are supporting evidence only; selector telemetry is primary.",
        "No motif is promoted by visual inspection without selector-backed telemetry evidence.",
        "Source-derived graph elements are visually distinct from runtime-added elements.",
        "",
        "## Source/Runtime Graph Distinction",
        "",
        "- Source-derived nodes: colored fill with dark border.",
        "- Runtime-added nodes: white fill with red border.",
        "- Dense graph output: checkpoint sequence, animation, layout JSON, and final HTML.",
        "- Sparse graph output: GRCL-9V3 role overlay and source/runtime boundary panel.",
        "",
        "## Visual Legend",
        "",
        "- Red dashed edges are explicit GRCL-9V3 bridge edges.",
        "- Node labels show node id and lowered motif role.",
        "- Behavior plots and graph snapshots are read from saved telemetry artifacts.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _visual_index(session: GRCL9V3VisualReviewSession) -> Mapping[str, Any]:
    return {
        "visualization_version": GRCL9V3_VISUALIZATION_VERSION,
        "family": "grcl9v3",
        "session_id": session.session_id,
        "selector_session_id": session.selector_session_id,
        "records": [record.to_mapping() for record in session.records],
        "skipped_records": [record.to_mapping() for record in session.skipped_records],
        "visual_claim_boundary": "supporting evidence only; selector telemetry is primary",
        "no_visual_only_promotion": True,
    }


def _session_manifest(
    session: GRCL9V3VisualReviewSession,
    output_root: Path,
) -> Mapping[str, Any]:
    command = (
        "PYTHONPATH=src python -m pygrc.visualization.grcl9v3_lowering "
        f"--session-id {session.session_id} "
        f"--selector-session-id {session.selector_session_id} "
        f"--output-root {output_root}"
    )
    return {
        "session_id": session.session_id,
        "session_kind": "grcl9v3_visual_review",
        "visualization_version": GRCL9V3_VISUALIZATION_VERSION,
        "family": "grcl9v3",
        "source_session_ids": list(session.source_session_ids),
        "selector_session_id": session.selector_session_id,
        "replay_command": command,
        "input_paths": [str(output_root / "sessions" / session.selector_session_id)],
        "output_paths": [
            str(session.visual_index_path),
            str(session.report_path),
            str(session.summary_path),
        ],
        "observation_summary": (
            f"Rendered {len(session.records)} selector-backed visual records; "
            f"skipped {len(session.skipped_records)} non-motif selector records."
        ),
        "visual_claim_boundary": "supporting evidence only; selector telemetry is primary",
        "no_visual_only_promotion": True,
    }


def _write_summary_markdown(
    path: Path,
    session: GRCL9V3VisualReviewSession,
) -> None:
    lines = [
        f"# {session.session_id} GRCL-9V3 Visual Review Summary",
        "",
        "## Scope",
        "",
        f"- Selector session: `{session.selector_session_id}`",
        f"- Source sessions: `{', '.join(session.source_session_ids)}`",
        f"- Rendered selector-backed records: `{len(session.records)}`",
        f"- Skipped non-motif records: `{len(session.skipped_records)}`",
        "- Claim boundary: visuals are supporting evidence only; selector telemetry is primary.",
        "",
        "## Rendered Records",
        "",
        "| Fixture | Label | Score | Connected | Bridges | Overlay | Boundary |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for record in session.records:
        overlay = Path(record.grcl9v3_overlay_path)
        boundary = Path(record.boundary_panel_path)
        lines.append(
            f"| `{record.fixture_name}` | `{record.confidence_label}` | "
            f"{record.confidence_score} | `{record.connected}` | "
            f"{record.bridge_edge_count} | [overlay]({overlay}) | "
            f"[boundary]({boundary}) |"
        )
    lines.extend(["", "## Skipped Records", "", "| Fixture | Label | Reason |", "|---|---|---|"])
    for record in session.skipped_records:
        lines.append(
            f"| `{record.fixture_name}` | `{record.confidence_label}` | `{record.reason}` |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_readme(root: Path, session: GRCL9V3VisualReviewSession) -> None:
    lines = [
        f"# {session.session_id}. GRCL-9V3 Visual Review",
        "",
        "Status: `completed`",
        "",
        "This session renders visual artifacts for selector-backed lowered-source motif records.",
        "Visuals are supporting evidence only; selector telemetry remains the primary evidence surface.",
        "",
        "Primary artifacts:",
        "",
        "- `visual_index.json`",
        "- `reports/visual_review_report.json`",
        "- `reports/visual_review_summary.md`",
        "- `visualizations/`",
    ]
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_experimental_log(path: Path, session: GRCL9V3VisualReviewSession) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = (
        f"| {session.session_id} | Visual review over {session.selector_session_id} | "
        f"{len(session.records)} | 0 | `{session.session_root}` |"
    )
    existing_rows: list[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("| S") and line[3:4].isdigit():
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if cells and cells[0] != session.session_id:
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
    path.write_text("\n".join(lines), encoding="utf-8")


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json_dumps(payload), encoding="utf-8")


def _validate_session_id(session_id: str) -> None:
    if not session_id.startswith("S") or not session_id[1:].isdigit():
        raise ValueError("session ids must use S0001-style formatting")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render GRCL-9V3 lowered-source visual review artifacts.",
    )
    parser.add_argument("--session-id", default="S0003")
    parser.add_argument("--selector-session-id", default="S0002")
    parser.add_argument("--output-root", default=str(GRCL9V3_REPLAY_ROOT))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    session = render_grcl9v3_lowering_visual_review(
        session_id=args.session_id,
        selector_session_id=args.selector_session_id,
        output_root=Path(args.output_root),
    )
    print(json.dumps(session.to_mapping(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "GRCL9V3_BOUNDARY_PANEL_FILENAME",
    "GRCL9V3_OVERLAY_FILENAME",
    "GRCL9V3_OVERLAY_SUMMARY_FILENAME",
    "GRCL9V3_VISUALIZATION_VERSION",
    "GRCL9V3SkippedVisualRecord",
    "GRCL9V3VisualLaneRecord",
    "GRCL9V3VisualReviewSession",
    "render_grcl9v3_lowering_visual_review",
]
