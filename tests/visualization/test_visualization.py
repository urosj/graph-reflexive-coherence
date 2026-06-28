"""Visualization tests for behavior and graph rendering surfaces."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import pygrc
from pygrc import telemetry, visualization
from pygrc.cli.grc9_landscape_visuals import main as grc9_landscape_visuals_main
from pygrc.cli.grc9_representative_visuals import main as grc9_representative_visuals_main
from pygrc.cli.grc9v3_representative_visuals import main as grc9v3_representative_visuals_main
from pygrc.cli.grcv2_representative_graphs import main as representative_graphs_main
from pygrc.cli.grcv3_landscape_visuals import main as grcv3_landscape_visuals_main
from pygrc.cli.grcv3_representative_visuals import main as grcv3_representative_visuals_main
from pygrc.cli.grcv2_representative_visuals import main as representative_visuals_main
from pygrc.core import GRCEvent, StepResult
from pygrc.visualization import graph_render as graph_render_module
from pygrc.visualization import representative as representative_module
from pygrc.visualization import render as render_module


def _synthetic_graph_checkpoints(
    identity: telemetry.RunTelemetryIdentity,
) -> tuple[telemetry.GraphCheckpointArtifact, ...]:
    return (
        telemetry.GraphCheckpointArtifact(
            identity=identity,
            checkpoint_id="cp-initial",
            step_index=0,
            time=0.0,
            checkpoint_label="initial",
            graph_kind="weighted_graph",
            node_count=2,
            edge_count=1,
            node_records=(
                {
                    "node_id": 0,
                    "coherence": 1.0,
                    "sink_flag": True,
                    "payload": {
                        "primitive_id": "cell-a",
                        "primitive_type": "basin",
                        "role": "identity_core",
                        "chart_center_hint": [0.0, 0.0],
                    },
                },
                {
                    "node_id": 1,
                    "coherence": 0.6,
                    "collapse_flag": True,
                    "collapsed_sink_id": "0",
                    "collapse_winner_margin": 0.22,
                    "collapsed_step_index": 2,
                    "payload": {
                        "primitive_id": "cell-b",
                        "primitive_type": "junction",
                        "role": "routing_hub",
                        "chart_center_hint": [1.0, 0.0],
                        "is_hostless": True,
                    },
                },
            ),
            edge_records=(
                {
                    "edge_id": 0,
                    "source_node_id": 0,
                    "target_node_id": 1,
                    "base_conductance": 0.8,
                    "signed_flux_source": 0.2,
                    "payload": {
                        "primitive_id": "ridge-1",
                        "primitive_type": "ridge",
                        "role": "boundary_support",
                    },
                    "directionality_semantics": "support_only",
                    "geometric_length_available": True,
                    "geometric_length": 1.0,
                },
            ),
        ),
        telemetry.GraphCheckpointArtifact(
            identity=identity,
            checkpoint_id="cp-step-2",
            step_index=2,
            time=0.2,
            checkpoint_label="step_2",
            graph_kind="weighted_graph",
            node_count=3,
            edge_count=2,
            node_records=(
                {
                    "node_id": 0,
                    "coherence": 0.9,
                    "sink_flag": True,
                    "payload": {
                        "primitive_id": "cell-a",
                        "primitive_type": "basin",
                        "role": "identity_core",
                        "chart_center_hint": [0.0, 0.0],
                    },
                },
                {
                    "node_id": 1,
                    "coherence": 0.7,
                    "choice_flag": True,
                    "choice_viable_sink_ids": ["0", "2"],
                    "choice_winner_sink_id": "0",
                    "choice_winner_margin": 0.08,
                    "payload": {
                        "primitive_id": "cell-b",
                        "primitive_type": "junction",
                        "role": "routing_hub",
                        "chart_center_hint": [1.0, 0.0],
                        "is_hostless": True,
                    },
                },
                {
                    "node_id": 2,
                    "coherence": 0.4,
                    "payload": {
                        "primitive_id": "cell-c",
                        "primitive_type": "plateau",
                        "role": "meta_stable_region",
                        "chart_center_hint": [0.5, 0.8],
                    },
                },
            ),
            edge_records=(
                {
                    "edge_id": 0,
                    "source_node_id": 0,
                    "target_node_id": 1,
                    "base_conductance": 0.7,
                    "signed_flux_source": 0.15,
                    "payload": {
                        "primitive_id": "ridge-1",
                        "primitive_type": "ridge",
                        "role": "boundary_support",
                    },
                    "directionality_semantics": "support_only",
                    "geometric_length_available": True,
                    "geometric_length": 1.0,
                },
                {
                    "edge_id": 1,
                    "source_node_id": 1,
                    "target_node_id": 2,
                    "base_conductance": 0.5,
                    "signed_flux_source": -0.1,
                    "payload": {
                        "primitive_id": "valley-1",
                        "primitive_type": "valley",
                        "role": "transport_channel",
                    },
                    "directionality_semantics": "transport_channel",
                    "geometric_length_available": False,
                },
            ),
            event_count_window=1,
            event_counts_by_kind_window={"birth": 1, "collapse": 1},
            flow_representation="signed_edge_flux",
        ),
    )


def _synthetic_run_pack(
    output_root: Path,
    *,
    with_graph_checkpoints: bool = False,
) -> telemetry.TelemetryArtifactPack:
    identity = telemetry.RunTelemetryIdentity(
        run_id="run123",
        model_family="grcv2",
        params_identity="params123",
        seed_name="Synthetic-Cell",
        param_family="balanced_baseline",
        requested_steps=3,
    )
    step_results = [
        StepResult(
            step_index=1,
            time=0.1,
            events=[GRCEvent(kind="birth", step_index=1, source_family="grcv2")],
            observables={
                "budget_current": 1.0,
                "budget_error": 0.0,
                "num_nodes": 2,
                "num_edges": 1,
                "sink_count": 0,
                "birth_count": 1,
                "average_conductance": 0.8,
                "abundance": 1.0,
                "weighted_abundance": 1.5,
            },
        ),
        StepResult(
            step_index=2,
            time=0.2,
            events=[],
            observables={
                "budget_current": 1.0,
                "budget_error": 0.0,
                "num_nodes": 3,
                "num_edges": 2,
                "sink_count": 1,
                "birth_count": 1,
                "average_conductance": 0.7,
                "abundance": 2.0,
                "weighted_abundance": 3.0,
            },
        ),
    ]
    step_rows = tuple(
        telemetry.step_row_from_step_result(step_result, identity=identity)
        for step_result in step_results
    )
    event_rows = tuple(
        row
        for step_result in step_results
        for row in telemetry.event_rows_from_events(step_result.events, identity=identity)
    )
    summary = telemetry.run_summary_from_step_results(
        step_results,
        identity=identity,
        initial_observables={
            "budget_current": 1.0,
            "budget_error": 0.0,
            "num_nodes": 1,
            "num_edges": 0,
            "sink_count": 0,
            "birth_count": 0,
            "average_conductance": 0.9,
            "abundance": 0.0,
            "weighted_abundance": 0.0,
        },
        final_observables=dict(step_results[-1].observables),
        resolved_params={"dt": 0.1, "evolution": {"alpha": 0.5}},
        raw_params={"dt": 0.1, "evolution": {"alpha": 0.5}},
        parameter_overrides={},
    )
    report = telemetry.build_run_experiment_report(summary, step_rows=step_rows)
    layout = telemetry.build_telemetry_artifact_layout("run123", root_dir=output_root / "outputs")
    graph_checkpoints: tuple[telemetry.GraphCheckpointArtifact, ...] = ()
    graph_checkpoint_index: telemetry.GraphCheckpointIndex | None = None
    if with_graph_checkpoints:
        graph_checkpoints = _synthetic_graph_checkpoints(identity)
        graph_checkpoint_index = telemetry.GraphCheckpointIndex(
            identity=identity,
            selection_policy="initial+every_step+final",
            selection_params={"every_step": True},
            checkpoints=tuple(
                telemetry.GraphCheckpointReference(
                    checkpoint_id=checkpoint.checkpoint_id,
                    step_index=checkpoint.step_index,
                    time=checkpoint.time,
                    checkpoint_label=checkpoint.checkpoint_label,
                    path=f"{checkpoint.checkpoint_id}.json",
                )
                for checkpoint in graph_checkpoints
            ),
        )
    return telemetry.TelemetryArtifactPack(
        layout=layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=summary,
        experiment_report=report,
        comparison_report=None,
        graph_checkpoint_index=graph_checkpoint_index,
        graph_checkpoints=graph_checkpoints,
    )


def _synthetic_grc9v3_graph_checkpoints(
    identity: telemetry.RunTelemetryIdentity,
    *,
    with_overlays: bool = True,
) -> tuple[telemetry.GraphCheckpointArtifact, ...]:
    family_extensions = (
        {
            "grc9v3": {
                "contract_version": telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                "checkpoint_surface": "phase_t_grc9v3_iter6_overlays",
                "overlay_status": "enabled",
                "node_overlay": {
                    "11": {
                        "coherence": 1.0,
                        "gradient_norm": 0.25,
                        "min_signed_hessian": -0.2,
                        "basin_id": "11",
                        "parent_id": None,
                        "depth": 0,
                        "is_sink": True,
                        "is_geometric_seed": True,
                        "is_module_node": False,
                        "spark_lane": telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
                        "column_h": [-1.5, 1.0, -2.5],
                        "min_abs_column_h": 1.0,
                        "min_abs_column_h_column": 2,
                        "column_h_branch_hit": True,
                        "column_h_gate_reasons": ["column_h_threshold_hit"],
                    },
                    "12": {
                        "coherence": 0.5,
                        "gradient_norm": 0.1,
                        "min_signed_hessian": 0.05,
                        "basin_id": "12",
                        "parent_id": "11",
                        "depth": 1,
                        "is_sink": True,
                        "is_geometric_seed": False,
                        "is_module_node": True,
                    },
                },
                "port_overlay": {
                    "by_node": {
                        "11": {
                            "occupied_ports": [1, 2, 3, 4, 5, 6, 7, 8, 9],
                            "free_ports": [],
                            "active_degree": 9,
                            "saturated": True,
                        },
                        "12": {
                            "occupied_ports": [1],
                            "free_ports": [2, 3, 4, 5, 6, 7, 8, 9],
                            "active_degree": 1,
                            "saturated": False,
                        },
                    },
                    "row_totals": [4, 3, 3],
                    "column_totals": [4, 3, 3],
                    "saturated_node_ids": [11],
                },
                "edge_overlay": {
                    "21": {
                        "base_conductance": 1.0,
                        "flux_uv": 0.2,
                        "geometric_length": 1.0,
                        "temporal_delay": None,
                        "flux_coupling": None,
                    }
                },
                "module_overlay": {
                    "expansions": {
                        "1": {
                            "parent_sink_id": 11,
                            "module_node_ids": [12, 13, 14, 15, 16],
                            "expansion_step": 1,
                            "distribution_weights": [0.33, 0.33, 0.34],
                        }
                    },
                    "latest": {
                        "module_sink_ids": [12, 16],
                        "stabilized_child_node_ids": [12, 16],
                        "stable_child_basin_count": 2,
                    },
                },
                "choice_overlay": {
                    "choice_regime_nodes": [14],
                    "choice_registry": {"14": {"node_id": 14, "sink_ids": [12, 16]}},
                    "collapse_registry": {"14": {"collapsed_sink_id": 12}},
                    "learned_basin_ids": {"14": "12"},
                },
            }
        }
        if with_overlays
        else {
            "grc9v3": {
                "contract_version": telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                "checkpoint_surface": "phase_t_grc9v3_iter6_overlays",
                "overlay_status": "disabled",
            }
        }
    )
    return (
        telemetry.GraphCheckpointArtifact(
            identity=identity,
            checkpoint_id="step-00000000",
            step_index=0,
            time=0.0,
            checkpoint_label="initial",
            graph_kind="port_graph",
            node_count=2,
            edge_count=1,
            node_records=(
                {
                    "node_id": 11,
                    "role": "spark_candidate_parent",
                    "coherence": 1.0,
                    "basin_id": "11",
                    "parent_id": None,
                    "depth": 0,
                    "is_sink": True,
                    "active_degree": 9,
                    "payload": {"role": "spark_candidate_parent"},
                },
                {
                    "node_id": 12,
                    "role": "daughter_sink",
                    "coherence": 0.5,
                    "basin_id": "12",
                    "parent_id": "11",
                    "depth": 1,
                    "is_sink": True,
                    "active_degree": 1,
                    "payload": {"role": "daughter_sink"},
                },
            ),
            edge_records=(
                {
                    "edge_id": 21,
                    "source_node_id": 11,
                    "source_port_id": 1,
                    "target_node_id": 12,
                    "target_port_id": 2,
                    "conductance": 1.0,
                    "base_conductance": 1.0,
                    "signed_flux_source_to_target": 0.2,
                    "role": "module_internal",
                },
            ),
            family_extensions=family_extensions,
        ),
        telemetry.GraphCheckpointArtifact(
            identity=identity,
            checkpoint_id="step-00000002",
            step_index=2,
            time=0.2,
            checkpoint_label="step_2",
            graph_kind="port_graph",
            node_count=2,
            edge_count=1,
            node_records=(
                {
                    "node_id": 12,
                    "role": "daughter_sink",
                    "coherence": 0.55,
                    "basin_id": "12",
                    "parent_id": "11",
                    "depth": 1,
                    "is_sink": True,
                    "active_degree": 1,
                    "payload": {"role": "daughter_sink"},
                },
                {
                    "node_id": 14,
                    "role": "choice_node",
                    "coherence": 0.2,
                    "basin_id": "12",
                    "parent_id": "11",
                    "depth": 1,
                    "is_sink": False,
                    "choice_flag": True,
                    "collapse_flag": True,
                    "collapsed_sink_id": "12",
                    "active_degree": 2,
                    "payload": {"role": "choice_node"},
                },
            ),
            edge_records=(
                {
                    "edge_id": 22,
                    "source_node_id": 14,
                    "source_port_id": 1,
                    "target_node_id": 12,
                    "target_port_id": 4,
                    "conductance": 0.8,
                    "base_conductance": 0.8,
                    "signed_flux_source_to_target": -0.1,
                    "role": "choice_support",
                },
            ),
            event_count_window=2,
            event_counts_by_kind_window={"choice_detected": 1, "collapse": 1},
            family_extensions=family_extensions,
        ),
    )


def _synthetic_grc9v3_run_pack(
    output_root: Path,
    *,
    root_dir: Path | None = None,
    with_graph_checkpoints: bool = False,
    with_checkpoint_overlays: bool = True,
) -> telemetry.TelemetryArtifactPack:
    identity = telemetry.RunTelemetryIdentity(
        run_id="grc9v3-run123",
        model_family="grc9v3",
        params_identity="params123",
        seed_name="appendix_e_cell_division",
        param_family="phase7_appendix_e",
        requested_steps=2,
    )
    grc9v3_extension_step_1 = {
        "contract_version": telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
        "port_chart": {
            "num_nodes": 12,
            "num_port_edges": 11,
            "saturated_node_count": 1,
        },
        "row_basis_differential": {
            "gradient_norm_mean": 0.2,
            "signed_hessian_mean": -0.1,
            "current_min_signed_hessian_min": -0.3,
        },
        "hybrid_tensor": {
            "tensor_trace_mean": 1.5,
            "tensor_anisotropy_max": 0.7,
        },
        "transport": {"flux_abs_sum": 0.4},
        "identity_basin": {
            "sink_count": 1,
            "basin_count": 1,
            "daughter_sink_count": 0,
        },
        "hierarchy_state": {"max_hierarchy_depth": 0},
        "hybrid_spark_state": {
            "hybrid_spark_candidate_count": 1,
            "completed_hybrid_spark_count": 0,
            "candidate_pass_rate": 1.0,
            "last_candidate_spark_lane": telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
            "last_candidate_min_abs_column_h": 1.0,
            "last_candidate_column_h_branch_hit": True,
        },
        "choice_collapse": {
            "choice_regime_count": 0,
            "collapse_registry_count": 0,
        },
        "growth_state": {"growth_event_count": 0},
        "budget_correction": {"budget_error": 0.0},
    }
    grc9v3_extension_step_2 = {
        "contract_version": telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
        "port_chart": {
            "num_nodes": 16,
            "num_port_edges": 15,
            "saturated_node_count": 0,
        },
        "row_basis_differential": {
            "gradient_norm_mean": 0.3,
            "signed_hessian_mean": 0.05,
            "current_min_signed_hessian_min": -0.05,
        },
        "hybrid_tensor": {
            "tensor_trace_mean": 1.1,
            "tensor_anisotropy_max": 0.4,
        },
        "transport": {"flux_abs_sum": 0.9},
        "identity_basin": {
            "sink_count": 2,
            "basin_count": 2,
            "daughter_sink_count": 2,
        },
        "hierarchy_state": {"max_hierarchy_depth": 1},
        "hybrid_spark_state": {
            "hybrid_spark_candidate_count": 0,
            "completed_hybrid_spark_count": 1,
        },
        "choice_collapse": {
            "choice_regime_count": 1,
            "collapse_registry_count": 1,
        },
        "growth_state": {"growth_event_count": 0},
        "budget_correction": {"budget_error": 0.0},
    }
    step_rows = (
        telemetry.StepTelemetryRow(
            identity=identity,
            step_index=1,
            time=0.1,
            event_count=1,
            event_counts_by_kind={"hybrid_spark_candidate": 1},
            observables={"event_count": 1, "budget_error": 0.0},
            family_extensions={"grc9v3": grc9v3_extension_step_1},
        ),
        telemetry.StepTelemetryRow(
            identity=identity,
            step_index=2,
            time=0.2,
            event_count=4,
            event_counts_by_kind={
                "hybrid_expansion": 1,
                "hybrid_spark_completed": 1,
                "choice_detected": 1,
                "collapse": 1,
            },
            observables={"event_count": 4, "budget_error": 0.0},
            family_extensions={"grc9v3": grc9v3_extension_step_2},
        ),
    )
    lane_b_candidate_payload = {
        "spark_lane": telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
        "column_h_branch_hit": True,
        "gate_reasons": ["column_h_threshold_hit"],
    }
    event_rows = (
        telemetry.EventTelemetryRow(
            identity=identity,
            step_index=1,
            event_index=0,
            event_kind="hybrid_spark_candidate",
            source_family="GRC9V3",
            payload=lane_b_candidate_payload,
            family_extensions={
                "grc9v3": {"spark_evidence": lane_b_candidate_payload}
            },
        ),
    )
    grc9v3_run_extension = {
        "contract_version": telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
        "lifecycle_event_counts": {
            "spark_candidate_count": 1,
            "expansion_count": 1,
            "completed_spark_count": 1,
            "choice_detected_count": 1,
            "collapse_count": 1,
        },
        "representative_appendix_e_summary": {
            "fixture_name": "appendix_e_cell_division",
            "spark_completed": True,
            "daughter_sink_count": 2,
            "daughter_sink_node_ids": [12, 16],
            "module_basin_mass": {"12": 0.5, "16": 0.5},
            "hierarchy_parent": "11",
            "hierarchy_children": ["12", "16"],
            "budget_preserved": True,
            "replay_digest_match": True,
        },
    }
    summary = telemetry.RunTelemetrySummary(
        identity=identity,
        completed_steps=2,
        final_step_index=2,
        initial_time=0.0,
        final_time=0.2,
        total_event_count=5,
        event_counts_by_kind={
            "hybrid_spark_candidate": 1,
            "hybrid_expansion": 1,
            "hybrid_spark_completed": 1,
            "choice_detected": 1,
            "collapse": 1,
        },
        initial_observables={"event_count": 0, "budget_error": 0.0},
        final_observables={"event_count": 4, "budget_error": 0.0},
        resolved_params={},
        raw_params={},
        parameter_overrides={},
        family_extensions={"grc9v3": grc9v3_run_extension},
    )
    layout = telemetry.build_telemetry_artifact_layout(
        "grc9v3-run123",
        root_dir=root_dir or output_root / "outputs",
    )
    graph_checkpoints: tuple[telemetry.GraphCheckpointArtifact, ...] = ()
    graph_checkpoint_index: telemetry.GraphCheckpointIndex | None = None
    if with_graph_checkpoints:
        graph_checkpoints = _synthetic_grc9v3_graph_checkpoints(
            identity,
            with_overlays=with_checkpoint_overlays,
        )
        graph_checkpoint_index = telemetry.GraphCheckpointIndex(
            identity=identity,
            selection_policy="initial+every_step",
            selection_params={"include_initial": True, "every_step": True},
            checkpoints=tuple(
                telemetry.GraphCheckpointReference(
                    checkpoint_id=checkpoint.checkpoint_id,
                    step_index=checkpoint.step_index,
                    time=checkpoint.time,
                    checkpoint_label=checkpoint.checkpoint_label,
                    path=f"{checkpoint.checkpoint_id}.json",
                )
                for checkpoint in graph_checkpoints
            ),
        )
    report = telemetry.TelemetryExperimentReport(
        family="grc9v3",
        common={
            "report_type": "trajectory_summary_v1",
            "run_id": identity.run_id,
            "model_family": identity.model_family,
            "params_identity": identity.params_identity,
            "resolved_params": {},
            "raw_params": {},
            "parameter_overrides": {},
            "seed_name": identity.seed_name,
            "seed_source_reference": identity.seed_source_reference,
            "seed_path": identity.seed_path,
            "param_family": identity.param_family,
            "rng_seed": identity.rng_seed,
            "requested_steps": identity.requested_steps,
            "completed_steps": summary.completed_steps,
            "final_step_index": summary.final_step_index,
            "initial_time": summary.initial_time,
            "final_time": summary.final_time,
            "total_event_count": summary.total_event_count,
            "event_counts_by_kind": summary.event_counts_by_kind,
            "changed_observables": ["event_count"],
            "checkpoint_overview": {
                "step_count": len(step_rows),
                "first_step_index": 1,
                "last_step_index": 2,
            },
            "fixture_name": "appendix_e_cell_division",
            "final_snapshot_digest": "digest-final",
            "replay_final_snapshot_digest": "digest-replay",
            "replay_step_rows_match": True,
            "replay_event_rows_match": True,
            "replay_digest_match": True,
            "checkpoint_count": 0,
        },
        extensions={
            "grc9v3": {
                "contract_version": telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                "representative_fixture": "appendix_e_cell_division",
                "phase7_runtime_source": "scripts/run_grc9v3_representative_runtime.py",
            }
        },
    )
    return telemetry.TelemetryArtifactPack(
        layout=layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=summary,
        experiment_report=report,
        graph_checkpoint_index=graph_checkpoint_index,
        graph_checkpoints=graph_checkpoints,
    )


def _synthetic_lgrc9v3_graph_checkpoints(
    identity: telemetry.RunTelemetryIdentity,
) -> tuple[telemetry.GraphCheckpointArtifact, ...]:
    extension = {
        "lgrc9v3": {
            "contract_version": telemetry.LGRC9V3_TELEMETRY_CONTRACT_VERSION,
            "checkpoint_schema_version": telemetry.LGRC9V3_GRAPH_CHECKPOINT_SCHEMA_VERSION,
            "checkpoint_surface": telemetry.LGRC9V3_GRAPH_CHECKPOINT_SURFACE,
            "causal_clocks": {
                "scheduler_event_index": 2,
                "checkpoint_index": 2,
                "event_time_key": 2.0,
                "node_proper_time": {"0": 2.0, "1": 1.0, "2": 2.0},
                "node_last_update_proper_time": {"0": 2.0, "1": 1.0, "2": 2.0},
                "node_last_update_event_time_key": {"0": 2.0, "1": 1.0, "2": 2.0},
                "lapse": {"0": 1.0, "1": 1.0, "2": 1.0},
            },
            "edge_causal_delay": {"0": 1.0, "1": 1.5},
            "packet_ledger": {
                "in_flight_packet_total": 0.25,
                "conserved_budget_total": 3.0,
                "packet_records": [
                    {
                        "packet_id": "packet-0",
                        "packet_state": "in_flight",
                        "source_node_id": 0,
                        "target_node_id": 1,
                        "edge_id": 0,
                        "amount": 0.25,
                        "departure_event_time_key": 1.0,
                        "arrival_event_time_key": 2.0,
                    }
                ],
            },
            "topology_history": {
                "topology_event_count": 2,
                "topology_event_log": [
                    {
                        "kind": "lgrc9v3_causal_boundary_birth",
                        "payload": {
                            "parent_node_id": 0,
                            "child_node_id": 2,
                            "event_time_key": 2.0,
                        },
                    },
                    {
                        "kind": "lgrc9v3_proper_time_identity_acceptance",
                        "payload": {
                            "topology_event_kind": (
                                "lgrc9v3_proper_time_identity_acceptance"
                            ),
                            "sink_node_id": 0,
                            "identity_clock_policy": "sink_local_proper_time",
                            "observed_persistence_duration": 4.0,
                            "proper_time_persistence_threshold": 3.0,
                        },
                    },
                ],
            },
            "causal_spark": {
                "causal_spark_evaluation_index": 1,
                "causal_spark_diagnostic_log": [],
            },
        }
    }
    checkpoint = telemetry.GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id="lgrc-step-000002",
        step_index=2,
        time=2.0,
        checkpoint_label="causal_step_2",
        graph_kind="port_graph",
        node_count=3,
        edge_count=2,
        node_records=(
            {
                "node_id": 0,
                "coherence": 1.2,
                "is_sink": True,
                "node_proper_time": 2.0,
                "node_last_update_proper_time": 2.0,
                "node_last_update_event_time_key": 2.0,
                "lapse": 1.0,
                "payload": {"role": "causal_sink"},
            },
            {
                "node_id": 1,
                "coherence": 0.8,
                "node_proper_time": 1.0,
                "node_last_update_proper_time": 1.0,
                "node_last_update_event_time_key": 1.0,
                "lapse": 1.0,
                "payload": {"role": "packet_target"},
            },
            {
                "node_id": 2,
                "coherence": 0.2,
                "node_proper_time": 2.0,
                "node_last_update_proper_time": 2.0,
                "node_last_update_event_time_key": 2.0,
                "lapse": 1.0,
                "payload": {"role": "causal_boundary_child"},
            },
        ),
        edge_records=(
            {
                "edge_id": 0,
                "source_node_id": 0,
                "source_port_id": 1,
                "target_node_id": 1,
                "target_port_id": 1,
                "conductance": 1.0,
                "base_conductance": 1.0,
                "flux_uv": 0.25,
                "geometric_length": 1.0,
                "temporal_delay": 1.0,
                "edge_causal_delay": 1.0,
            },
            {
                "edge_id": 1,
                "source_node_id": 0,
                "source_port_id": 2,
                "target_node_id": 2,
                "target_port_id": 1,
                "conductance": 1.0,
                "base_conductance": 1.0,
                "flux_uv": 0.0,
                "geometric_length": 1.0,
                "temporal_delay": 1.5,
                "edge_causal_delay": 1.5,
            },
        ),
        event_count_window=3,
        event_counts_by_kind_window={
            "lgrc9v3_packet_arrival": 1,
            "lgrc9v3_causal_boundary_birth": 1,
            "lgrc9v3_proper_time_identity_acceptance": 1,
        },
        family_extensions=extension,
    )
    initial = telemetry.GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id="lgrc-step-000000",
        step_index=0,
        time=0.0,
        checkpoint_label="initial",
        graph_kind="port_graph",
        node_count=2,
        edge_count=1,
        node_records=checkpoint.node_records[:2],
        edge_records=checkpoint.edge_records[:1],
        family_extensions=extension,
    )
    return (initial, checkpoint)


def _synthetic_lgrc9v3_run_pack(output_root: Path) -> telemetry.TelemetryArtifactPack:
    identity = telemetry.RunTelemetryIdentity(
        run_id="lgrc9v3-run123",
        model_family="LGRC9V3",
        params_identity="params-lgrc",
        seed_name="lgrc9v3-causal-fixture",
    )
    step_rows = (
        telemetry.StepTelemetryRow(
            identity=identity,
            step_index=1,
            time=1.0,
            event_count=1,
            event_counts_by_kind={"lgrc9v3_packet_departure": 1},
            observables={
                "scheduler_event_index": 1,
                "checkpoint_index": 1,
                "event_time_key": 1.0,
                "packet_count": 1,
                "event_queue_length": 1,
                "in_flight_packet_total": 0.25,
                "conserved_budget_total": 3.0,
            },
            family_extensions={
                "lgrc9v3": {
                    "scheduler_event_index": 1,
                    "checkpoint_index": 1,
                    "event_time_key": 1.0,
                    "packet_ledger": {
                        "in_flight_packet_total": 0.25,
                        "event_queue_length": 1,
                    },
                    "local_update_count": 0,
                    "causal_spark_evaluation_index": 0,
                    "causal_spark_diagnostic_count": 0,
                    "topology_event_count": 0,
                }
            },
        ),
        telemetry.StepTelemetryRow(
            identity=identity,
            step_index=2,
            time=2.0,
            event_count=4,
            event_counts_by_kind={
                "lgrc9v3_packet_arrival": 1,
                "lgrc9v3_local_update": 1,
                "lgrc9v3_causal_spark_candidate": 1,
                "lgrc9v3_causal_boundary_birth": 1,
            },
            observables={
                "scheduler_event_index": 2,
                "checkpoint_index": 2,
                "event_time_key": 2.0,
                "packet_count": 1,
                "event_queue_length": 0,
                "in_flight_packet_total": 0.0,
                "conserved_budget_total": 3.0,
                "local_update_count": 1,
                "causal_spark_diagnostic_count": 1,
                "topology_event_count": 1,
            },
            family_extensions={
                "lgrc9v3": {
                    "scheduler_event_index": 2,
                    "checkpoint_index": 2,
                    "event_time_key": 2.0,
                    "packet_ledger": {
                        "in_flight_packet_total": 0.0,
                        "event_queue_length": 0,
                    },
                    "local_update_count": 1,
                    "causal_spark_evaluation_index": 1,
                    "causal_spark_diagnostic_count": 1,
                    "topology_event_count": 1,
                }
            },
        ),
    )
    event_rows = (
        telemetry.EventTelemetryRow(
            identity=identity,
            step_index=1,
            event_index=0,
            event_kind="lgrc9v3_packet_departure",
            source_family="LGRC9V3",
            payload={},
            family_extensions={
                "lgrc9v3": {
                    "event_domain": "packet",
                    "lifecycle_stage": "departure",
                }
            },
        ),
        telemetry.EventTelemetryRow(
            identity=identity,
            step_index=2,
            event_index=0,
            event_kind="lgrc9v3_causal_spark_candidate",
            source_family="LGRC9V3",
            payload={
                "spark_lane": telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
                "column_h_branch_hit": True,
                "gate_reasons": ["column_h_threshold_hit"],
            },
            family_extensions={
                "lgrc9v3": {
                    "event_domain": "spark",
                    "spark_lane": telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
                    "column_h_branch_hit": True,
                    "gate_reasons": ["column_h_threshold_hit"],
                }
            },
        ),
        telemetry.EventTelemetryRow(
            identity=identity,
            step_index=2,
            event_index=1,
            event_kind="lgrc9v3_causal_boundary_birth",
            source_family="LGRC9V3",
            payload={},
            family_extensions={
                "lgrc9v3": {
                    "event_domain": "topology",
                    "lifecycle_stage": "causal_boundary_birth",
                }
            },
        ),
    )
    summary = telemetry.RunTelemetrySummary(
        identity=identity,
        completed_steps=2,
        final_step_index=2,
        initial_time=0.0,
        final_time=2.0,
        total_event_count=5,
        event_counts_by_kind={
            "lgrc9v3_packet_departure": 1,
            "lgrc9v3_packet_arrival": 1,
            "lgrc9v3_local_update": 1,
            "lgrc9v3_causal_spark_candidate": 1,
            "lgrc9v3_causal_boundary_birth": 1,
        },
        initial_observables={"event_time_key": 0.0, "in_flight_packet_total": 0.0},
        final_observables={"event_time_key": 2.0, "in_flight_packet_total": 0.0},
        family_extensions={"lgrc9v3": {"topology_event_count": 1}},
    )
    report = telemetry.TelemetryExperimentReport(
        family="LGRC9V3",
        common={
            "run_id": identity.run_id,
            "seed_name": identity.seed_name,
            "param_family": identity.param_family,
            "completed_steps": summary.completed_steps,
            "total_event_count": summary.total_event_count,
            "changed_observables": ["event_time_key", "topology_event_count"],
            "params_identity": identity.params_identity,
            "resolved_params": {"dt": 1.0},
            "event_counts_by_kind": summary.event_counts_by_kind,
            "checkpoint_overview": {
                "step_count": len(step_rows),
                "first_step_index": 1,
                "last_step_index": 2,
            },
        },
        extensions={
            "lgrc9v3": {
                "contract_version": telemetry.LGRC9V3_TELEMETRY_CONTRACT_VERSION,
                "visual_surface_note": "causal_history_not_synchronous_slice",
            }
        },
    )
    return telemetry.TelemetryArtifactPack(
        layout=telemetry.build_telemetry_artifact_layout(
            identity.run_id,
            root_dir=output_root / "outputs",
        ),
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=summary,
        experiment_report=report,
        graph_checkpoint_index=None,
        graph_checkpoints=_synthetic_lgrc9v3_graph_checkpoints(identity),
    )


def _write_synthetic_grc9v3_artifact(
    output_root: Path,
    *,
    with_graph_checkpoints: bool = False,
    with_checkpoint_overlays: bool = True,
) -> telemetry.TelemetryArtifactPack:
    pack = _synthetic_grc9v3_run_pack(
        output_root,
        root_dir=(
            output_root
            / "outputs"
            / visualization.DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH
            / visualization.DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME
        ),
        with_graph_checkpoints=with_graph_checkpoints,
        with_checkpoint_overlays=with_checkpoint_overlays,
    )
    telemetry.save_telemetry_artifact_pack(
        pack.layout,
        step_rows=pack.step_rows,
        event_rows=pack.event_rows,
        run_summary=pack.run_summary,
        graph_checkpoint_index=pack.graph_checkpoint_index,
        graph_checkpoints=pack.graph_checkpoints,
    )
    if pack.experiment_report is not None:
        telemetry.save_experiment_report(pack.layout.experiment_report_path, pack.experiment_report)
    return pack


class VisualizationTest(unittest.TestCase):
    """Validate the artifact-driven visualization surfaces."""

    def test_top_level_package_exports_visualization(self) -> None:
        self.assertIs(pygrc.visualization, visualization)

    def test_map_telemetry_root_to_visualization_root_maps_legacy_tree_into_run_parent_root(self) -> None:
        mapped = visualization.map_telemetry_root_to_visualization_root(
            Path("outputs/telemetry/grcv2/representative")
        )
        self.assertEqual(Path("outputs/grcv2/representative"), mapped)

    def test_render_run_visual_bundle_writes_expected_pngs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _synthetic_run_pack(Path(temp_dir))
            layout = visualization.build_run_visualization_layout(
                pack.layout,
                visualization_root=Path(temp_dir) / "visualization" / "synthetic",
            )
            visualization.render_run_visual_bundle(pack, layout=layout)

            self.assertTrue(layout.trajectory_figure_path.exists())
            self.assertTrue(layout.event_timeline_path.exists())
            self.assertTrue(layout.report_panel_path.exists())

    def test_render_graph_run_visual_bundle_writes_snapshots_html_and_animation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _synthetic_run_pack(Path(temp_dir), with_graph_checkpoints=True)
            layout = visualization.build_graph_run_visualization_layout(
                pack.layout,
                visualization_root=Path(temp_dir) / "visualization" / "synthetic-graph",
            )
            visualization.render_graph_run_visual_bundle(pack, layout=layout)

            snapshot_paths = sorted(layout.snapshots_dir.glob("*.png"))
            self.assertEqual(2, len(snapshot_paths))
            self.assertTrue(layout.sequence_figure_path.exists())
            self.assertTrue(layout.animation_path.exists())
            self.assertTrue(layout.layout_json_path.exists())
            self.assertTrue(layout.final_html_path.exists())

    def test_edge_width_includes_flux_overlay_strength(self) -> None:
        context = graph_render_module._GraphRenderContext(
            coherence_min=0.0,
            coherence_max=1.0,
            conductance_max=1.0,
            flux_abs_max=1.0,
        )
        baseline_edge = {
            "base_conductance": 0.5,
        }
        active_edge = {
            "base_conductance": 0.5,
            "signed_flux_source": 0.75,
        }

        baseline_width = graph_render_module._edge_width(baseline_edge, context=context)
        active_width = graph_render_module._edge_width(active_edge, context=context)

        self.assertGreater(active_width, baseline_width)

    def test_directed_edge_endpoints_follow_signed_flux(self) -> None:
        positive_edge = {
            "source_node_id": 1,
            "target_node_id": 2,
            "signed_flux_source": 0.25,
        }
        negative_edge = {
            "source_node_id": 1,
            "target_node_id": 2,
            "signed_flux_source": -0.25,
        }
        zero_edge = {
            "source_node_id": 1,
            "target_node_id": 2,
            "signed_flux_source": 0.0,
        }

        self.assertEqual(
            (1, 2),
            graph_render_module._directed_edge_endpoints(positive_edge),
        )
        self.assertEqual(
            (2, 1),
            graph_render_module._directed_edge_endpoints(negative_edge),
        )
        self.assertIsNone(
            graph_render_module._directed_edge_endpoints(zero_edge),
        )

    def test_graph_render_requires_saved_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _synthetic_run_pack(Path(temp_dir), with_graph_checkpoints=False)
            layout = visualization.build_graph_run_visualization_layout(
                pack.layout,
                visualization_root=Path(temp_dir) / "visualization" / "missing-graph",
            )
            with self.assertRaises(ValueError) as ctx:
                visualization.render_graph_run_visual_bundle(pack, layout=layout)

            self.assertIn("record_graph_checkpoints=True", str(ctx.exception))

    def test_render_representative_visual_suite_writes_run_and_comparison_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv2_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                num_steps=3,
                family_name="balanced_baseline",
                rng_seed=7,
            )
            result = visualization.render_grcv2_representative_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                family_name="balanced_baseline",
            )

            self.assertEqual("behavior", result.surface_mode)
            self.assertTrue(result.cell1_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.cell1_visualization_layout.event_timeline_path.exists())
            self.assertTrue(result.cell1_visualization_layout.report_panel_path.exists())
            self.assertTrue(result.cell4_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.comparison_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.comparison_visualization_layout.report_panel_path.exists())
            self.assertIsNone(result.cell1_graph_visualization_layout)

    def test_grcv3_report_lines_include_family_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=3,
            )

            lines = render_module._build_run_report_lines(result.primary_report)

            self.assertTrue(any("family_extensions:" == line for line in lines))
            self.assertTrue(
                any(
                    "grcv3.final_basin_summary.active_basin_count:" in line
                    for line in lines
                )
            )
            self.assertTrue(
                any(
                    "grcv3.signed_hessian.hessian_sign:" in line
                    for line in lines
                )
            )

    def test_grcv3_comparison_report_lines_include_family_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=3,
            )

            lines = render_module._build_comparison_report_lines(result.comparison_report)

            self.assertTrue(any("family_extensions:" == line for line in lines))
            self.assertTrue(any("left.grcv3.contract_version:" in line for line in lines))
            self.assertTrue(any("right.grcv3.contract_version:" in line for line in lines))

    def test_grcv3_extension_trajectory_series_are_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=3,
            )
            xs, ys = render_module._trajectory_series(
                "family_extensions.grcv3.signed_hessian.hessian_sign",
                result.primary_run.telemetry.run_summary,
                result.primary_run.telemetry.step_rows,
            )

            self.assertEqual([1, 2, 3], xs)
            self.assertEqual(3, len(ys))
            self.assertTrue(all(value in (-1.0, 1.0) for value in ys))

    def test_grc9_observable_constants_are_exported(self) -> None:
        self.assertIn(
            "family_extensions.grc9.port_chart.num_nodes",
            visualization.DEFAULT_GRC9_RUN_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.grc9.identity_abundance.sink_count",
            visualization.DEFAULT_GRC9_COMPARISON_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.grc9.coarse_graining.coarse_fields_list.length",
            visualization.DEFAULT_GRC9_RUN_OBSERVABLES,
        )

    def test_grc9_extension_trajectory_series_are_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=3,
            )
            xs, ys = render_module._trajectory_series(
                "family_extensions.grc9.port_chart.num_nodes",
                result.primary_run.telemetry.run_summary,
                result.primary_run.telemetry.step_rows,
            )

            self.assertEqual([1, 2, 3], xs)
            self.assertEqual(3, len(ys))
            self.assertTrue(all(value > 0.0 for value in ys))

            coarse_xs, coarse_ys = render_module._trajectory_series(
                "family_extensions.grc9.coarse_graining.coarse_fields_list.length",
                result.primary_run.telemetry.run_summary,
                result.primary_run.telemetry.step_rows,
            )
            self.assertEqual([1, 2, 3], coarse_xs)
            self.assertEqual([0.0, 0.0, 0.0], coarse_ys)

    def test_grc9v3_observable_constants_are_exported(self) -> None:
        self.assertIn(
            "family_extensions.grc9v3.port_chart.num_nodes",
            visualization.DEFAULT_GRC9V3_RUN_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.grc9v3.hybrid_tensor.tensor_trace_mean",
            visualization.DEFAULT_GRC9V3_RUN_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.grc9v3.choice_collapse.collapse_registry_count",
            visualization.DEFAULT_GRC9V3_RUN_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.grc9v3.hybrid_spark_state.last_candidate_min_abs_column_h",
            visualization.DEFAULT_GRC9V3_RUN_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.grc9v3.hybrid_spark_state.last_candidate_column_h_branch_hit",
            visualization.DEFAULT_GRC9V3_RUN_OBSERVABLES,
        )
        self.assertNotIn(
            "family_extensions.grc9v3.hybrid_spark_state.last_candidate_spark_lane",
            visualization.DEFAULT_GRC9V3_RUN_OBSERVABLES,
        )

    def test_grc9v3_extension_trajectory_series_are_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _synthetic_grc9v3_run_pack(Path(temp_dir))
            xs, ys = render_module._trajectory_series(
                "family_extensions.grc9v3.port_chart.num_nodes",
                pack.run_summary,
                pack.step_rows,
            )

            self.assertEqual([1, 2], xs)
            self.assertEqual([12.0, 16.0], ys)

            tensor_xs, tensor_ys = render_module._trajectory_series(
                "family_extensions.grc9v3.hybrid_tensor.tensor_trace_mean",
                pack.run_summary,
                pack.step_rows,
            )
            self.assertEqual([1, 2], tensor_xs)
            self.assertEqual([1.5, 1.1], tensor_ys)

            column_h_xs, column_h_ys = render_module._trajectory_series(
                "family_extensions.grc9v3.hybrid_spark_state.last_candidate_min_abs_column_h",
                pack.run_summary,
                pack.step_rows,
            )
            self.assertEqual([1], column_h_xs)
            self.assertEqual([1.0], column_h_ys)

            branch_xs, branch_ys = render_module._trajectory_series(
                "family_extensions.grc9v3.hybrid_spark_state.last_candidate_column_h_branch_hit",
                pack.run_summary,
                pack.step_rows,
            )
            self.assertEqual([1], branch_xs)
            self.assertEqual([1.0], branch_ys)

    def test_grc9v3_event_categories_distinguish_lane_b_branch_attribution(self) -> None:
        identity = telemetry.RunTelemetryIdentity(
            run_id="lane-b-visual",
            model_family="grc9v3",
            params_identity="params",
        )
        lane_a = telemetry.EventTelemetryRow(
            identity=identity,
            step_index=1,
            event_index=0,
            event_kind="hybrid_spark_candidate",
            source_family="GRC9V3",
            payload={},
        )
        lane_b_signed = telemetry.EventTelemetryRow(
            identity=identity,
            step_index=2,
            event_index=0,
            event_kind="hybrid_spark_candidate",
            source_family="GRC9V3",
            payload={
                "spark_lane": telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
                "column_h_branch_hit": False,
                "gate_reasons": ["signed_hessian_hit"],
            },
        )
        lane_b_column = telemetry.EventTelemetryRow(
            identity=identity,
            step_index=3,
            event_index=0,
            event_kind="hybrid_spark_candidate",
            source_family="GRC9V3",
            payload={
                "spark_lane": telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
                "column_h_branch_hit": True,
                "gate_reasons": ["column_h_threshold_hit"],
            },
        )

        self.assertEqual(
            "lane_a_signed_hessian_candidate",
            render_module._event_visual_category(lane_a),
        )
        self.assertEqual(
            "lane_b_signed_hessian_candidate",
            render_module._event_visual_category(lane_b_signed),
        )
        self.assertEqual(
            "lane_b_column_h_branch_candidate",
            render_module._event_visual_category(lane_b_column),
        )

    def test_grc9v3_missing_optional_fields_do_not_crash_behavior_renderer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _synthetic_grc9v3_run_pack(Path(temp_dir))
            visualization_layout = visualization.build_run_visualization_layout(
                pack.layout,
                visualization_root=Path(temp_dir) / "visuals",
            )

            result = visualization.render_run_visual_bundle(
                pack,
                layout=visualization_layout,
                observables=visualization.DEFAULT_GRC9V3_RUN_OBSERVABLES,
            )

            self.assertTrue(result.trajectory_figure_path.exists())
            self.assertTrue(result.event_timeline_path.exists())

    def test_render_grc9v3_representative_visual_suite_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _write_synthetic_grc9v3_artifact(Path(temp_dir))

            result = visualization.render_grc9v3_representative_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                visualization_root=Path(temp_dir) / "visualization",
            )

            self.assertEqual("behavior", result.surface_mode)
            self.assertEqual("appendix_e_cell_division", result.fixture_name)
            self.assertEqual(pack.layout.run_id, result.telemetry_layout.run_id)
            self.assertTrue(result.visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.visualization_layout.event_timeline_path.exists())
            self.assertTrue(result.visualization_layout.report_panel_path.exists())

    def test_grc9v3_report_panel_includes_family_replay_and_appendix_e_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _write_synthetic_grc9v3_artifact(Path(temp_dir))

            result = visualization.render_grc9v3_representative_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                visualization_root=Path(temp_dir) / "visualization",
            )
            visual_report = representative_module._grc9v3_visual_report(pack)
            self.assertIsNotNone(visual_report)
            assert visual_report is not None
            lines = render_module._build_run_report_lines(visual_report)

            self.assertTrue(result.visualization_layout.report_panel_path.exists())
            self.assertIn("family_extensions:", lines)
            self.assertTrue(any("grc9v3.contract_version" in line for line in lines))
            self.assertIn("replay_digest_match: True", lines)
            self.assertTrue(
                any("representative_appendix_e_summary.daughter_sink_count" in line for line in lines)
            )
            self.assertTrue(
                any("representative_appendix_e_summary.hierarchy_parent" in line for line in lines)
            )
            self.assertTrue(
                any(
                    "visual_event_lane_summary.lane_b_column_h_branch_candidate" in line
                    for line in lines
                )
            )

    def test_grc9v3_representative_visual_suite_accepts_explicit_artifact_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _write_synthetic_grc9v3_artifact(Path(temp_dir))

            result = visualization.render_grc9v3_representative_visual_suite(
                telemetry_root=Path(temp_dir) / "missing",
                artifact_path=pack.layout.run_dir,
                visualization_root=Path(temp_dir) / "visualization",
            )

            self.assertEqual(pack.layout.run_id, result.telemetry_layout.run_id)
            self.assertTrue(result.visualization_layout.trajectory_figure_path.exists())

    def test_grc9v3_representative_visual_suite_rejects_graph_surface_without_checkpoints(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _write_synthetic_grc9v3_artifact(Path(temp_dir))

            with self.assertRaisesRegex(ValueError, "requires saved graph checkpoints"):
                visualization.render_grc9v3_representative_visual_suite(
                    telemetry_root=Path(temp_dir) / "outputs",
                    surface_mode=visualization.SURFACE_MODE_GRAPH,
                )

    def test_grc9v3_representative_visual_suite_writes_graph_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _write_synthetic_grc9v3_artifact(Path(temp_dir), with_graph_checkpoints=True)

            result = visualization.render_grc9v3_representative_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                visualization_root=Path(temp_dir) / "visualization",
                surface_mode=visualization.SURFACE_MODE_GRAPH,
            )

            self.assertIsNotNone(result.graph_visualization_layout)
            assert result.graph_visualization_layout is not None
            snapshot_paths = sorted(result.graph_visualization_layout.snapshots_dir.glob("*.png"))
            self.assertEqual(2, len(snapshot_paths))
            self.assertTrue(result.graph_visualization_layout.sequence_figure_path.exists())
            self.assertTrue(result.graph_visualization_layout.final_html_path.exists())
            self.assertTrue(result.graph_visualization_layout.animation_path.exists())
            self.assertTrue(result.graph_visualization_layout.layout_json_path.exists())
            pack = telemetry.load_telemetry_artifact_pack(result.telemetry_layout)
            grc9v3_overlay = pack.graph_checkpoints[0].family_extensions["grc9v3"]
            self.assertEqual("enabled", grc9v3_overlay["overlay_status"])
            self.assertIn("node_overlay", grc9v3_overlay)
            self.assertIn("port_overlay", grc9v3_overlay)
            self.assertIn("edge_overlay", grc9v3_overlay)
            self.assertIn("module_overlay", grc9v3_overlay)
            self.assertIn("choice_overlay", grc9v3_overlay)

    def test_grc9v3_graph_overlay_styles_lane_b_column_h_branch_nodes(self) -> None:
        identity = telemetry.RunTelemetryIdentity(
            run_id="grc9v3-graph-lane-b",
            model_family="grc9v3",
            params_identity="params",
        )
        checkpoint = _synthetic_grc9v3_graph_checkpoints(identity)[0]
        node_record = checkpoint.node_records[0]

        self.assertTrue(
            graph_render_module._node_has_column_h_branch(
                node_record,
                checkpoint=checkpoint,
            )
        )
        self.assertEqual(
            graph_render_module._COLUMN_H_BRANCH_EDGE,
            graph_render_module._node_edgecolor(node_record, checkpoint=checkpoint),
        )
        self.assertEqual(
            "11\nH",
            graph_render_module._node_label(node_record, checkpoint=checkpoint),
        )
        title = graph_render_module._node_title(node_record, checkpoint=checkpoint)
        self.assertIn("column_h_branch_hit=true", title)
        self.assertIn(telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE, title)

    def test_lgrc9v3_observable_constants_expose_causal_surfaces(self) -> None:
        self.assertIn(
            "family_extensions.lgrc9v3.event_time_key",
            visualization.DEFAULT_LGRC9V3_RUN_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.lgrc9v3.packet_ledger.in_flight_packet_total",
            visualization.DEFAULT_LGRC9V3_RUN_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.lgrc9v3.causal_spark_diagnostic_count",
            visualization.DEFAULT_LGRC9V3_RUN_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.lgrc9v3.topology_event_count",
            visualization.DEFAULT_LGRC9V3_RUN_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.lgrc9v3.multi_basin_formation.child_basin_state_record_count",
            visualization.DEFAULT_LGRC9V3_RUN_OBSERVABLES,
        )
        self.assertIn(
            "family_extensions.lgrc9v3.multi_basin_formation.failed_closed_control_count",
            visualization.DEFAULT_LGRC9V3_RUN_OBSERVABLES,
        )
        self.assertEqual(
            "checkpoint/event row",
            render_module._trajectory_x_label("LGRC9V3"),
        )
        self.assertEqual("step", render_module._trajectory_x_label("GRC9V3"))

    def test_lgrc9v3_extension_trajectory_series_are_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _synthetic_lgrc9v3_run_pack(Path(temp_dir))

            event_xs, event_ys = render_module._trajectory_series(
                "family_extensions.lgrc9v3.event_time_key",
                pack.run_summary,
                pack.step_rows,
            )
            self.assertEqual([1, 2], event_xs)
            self.assertEqual([1.0, 2.0], event_ys)

            packet_xs, packet_ys = render_module._trajectory_series(
                "family_extensions.lgrc9v3.packet_ledger.in_flight_packet_total",
                pack.run_summary,
                pack.step_rows,
            )
            self.assertEqual([1, 2], packet_xs)
            self.assertEqual([0.25, 0.0], packet_ys)

            spark_xs, spark_ys = render_module._trajectory_series(
                "family_extensions.lgrc9v3.causal_spark_diagnostic_count",
                pack.run_summary,
                pack.step_rows,
            )
            self.assertEqual([1, 2], spark_xs)
            self.assertEqual([0.0, 1.0], spark_ys)

    def test_lgrc9v3_event_categories_distinguish_causal_domains_and_lane_b_branch(
        self,
    ) -> None:
        identity = telemetry.RunTelemetryIdentity(
            run_id="lgrc9v3-visual-events",
            model_family="LGRC9V3",
            params_identity="params",
        )
        rows = {
            "packet": telemetry.EventTelemetryRow(
                identity=identity,
                step_index=1,
                event_index=0,
                event_kind="lgrc9v3_packet_arrival",
                source_family="LGRC9V3",
                payload={},
                family_extensions={"lgrc9v3": {"event_domain": "packet"}},
            ),
            "local_update": telemetry.EventTelemetryRow(
                identity=identity,
                step_index=1,
                event_index=1,
                event_kind="lgrc9v3_local_update",
                source_family="LGRC9V3",
                payload={},
                family_extensions={"lgrc9v3": {"event_domain": "local_update"}},
            ),
            "topology": telemetry.EventTelemetryRow(
                identity=identity,
                step_index=2,
                event_index=0,
                event_kind="lgrc9v3_causal_boundary_birth",
                source_family="LGRC9V3",
                payload={},
                family_extensions={"lgrc9v3": {"event_domain": "topology"}},
            ),
            "identity": telemetry.EventTelemetryRow(
                identity=identity,
                step_index=3,
                event_index=0,
                event_kind="lgrc9v3_proper_time_identity_acceptance",
                source_family="LGRC9V3",
                payload={},
                family_extensions={"lgrc9v3": {"event_domain": "identity"}},
            ),
            "lane_b_column": telemetry.EventTelemetryRow(
                identity=identity,
                step_index=4,
                event_index=0,
                event_kind="lgrc9v3_causal_spark_candidate",
                source_family="LGRC9V3",
                payload={},
                family_extensions={
                    "lgrc9v3": {
                        "event_domain": "spark",
                        "spark_lane": telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
                        "column_h_branch_hit": True,
                        "gate_reasons": ["column_h_threshold_hit"],
                    }
                },
            ),
            "lane_b_signed": telemetry.EventTelemetryRow(
                identity=identity,
                step_index=5,
                event_index=0,
                event_kind="lgrc9v3_causal_spark_candidate",
                source_family="LGRC9V3",
                payload={},
                family_extensions={
                    "lgrc9v3": {
                        "event_domain": "spark",
                        "spark_lane": telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
                        "column_h_branch_hit": False,
                        "gate_reasons": ["signed_hessian_hit"],
                    }
                },
            ),
            "lane_a": telemetry.EventTelemetryRow(
                identity=identity,
                step_index=6,
                event_index=0,
                event_kind="lgrc9v3_causal_spark_candidate",
                source_family="LGRC9V3",
                payload={},
                family_extensions={"lgrc9v3": {"event_domain": "spark"}},
            ),
        }

        self.assertEqual(
            "lgrc9v3_packet",
            render_module._event_visual_category(rows["packet"]),
        )
        self.assertEqual(
            "lgrc9v3_local_update",
            render_module._event_visual_category(rows["local_update"]),
        )
        self.assertEqual(
            "lgrc9v3_topology",
            render_module._event_visual_category(rows["topology"]),
        )
        self.assertEqual(
            "lgrc9v3_identity",
            render_module._event_visual_category(rows["identity"]),
        )
        self.assertEqual(
            "lgrc9v3_lane_b_column_h_branch_candidate",
            render_module._event_visual_category(rows["lane_b_column"]),
        )
        self.assertEqual(
            "lgrc9v3_lane_b_signed_hessian_candidate",
            render_module._event_visual_category(rows["lane_b_signed"]),
        )
        self.assertEqual(
            "lgrc9v3_lane_a_signed_hessian_candidate",
            render_module._event_visual_category(rows["lane_a"]),
        )

    def test_lgrc9v3_graph_renderer_exposes_causal_overlays(self) -> None:
        identity = telemetry.RunTelemetryIdentity(
            run_id="lgrc9v3-graph",
            model_family="LGRC9V3",
            params_identity="params",
        )
        checkpoint = _synthetic_lgrc9v3_graph_checkpoints(identity)[-1]
        positions = {0: (0.0, 0.0), 1: (1.0, 0.0), 2: (0.0, 1.0)}

        subtitle = graph_render_module._checkpoint_subtitle(checkpoint)
        self.assertIn("kappa=2", subtitle)
        self.assertIn("k=2", subtitle)
        self.assertIn("T_e=2.0", subtitle)
        self.assertIn("in_flight=0.25", subtitle)

        node_title = graph_render_module._node_title(
            checkpoint.node_records[0],
            checkpoint=checkpoint,
        )
        self.assertIn("node_proper_time=2.0", node_title)
        self.assertIn("node_last_update_event_time_key=2.0", node_title)
        self.assertIn("lgrc9v3_identity_acceptance=true", node_title)
        self.assertIn("identity_clock_policy=sink_local_proper_time", node_title)

        edge_title = graph_render_module._edge_title(
            checkpoint.edge_records[0],
            checkpoint=checkpoint,
        )
        self.assertIn("geometric_length=1.0", edge_title)
        self.assertIn("temporal_delay=1.0", edge_title)
        self.assertIn("edge_causal_delay=1.0", edge_title)
        self.assertIn("lgrc9v3_packet_count=1", edge_title)
        self.assertIn("lgrc9v3_in_flight_packet_count=1", edge_title)

        self.assertEqual(
            [(0, 2)],
            graph_render_module._lgrc9v3_topology_lineage_edges(
                checkpoint,
                positions=positions,
            ),
        )
        self.assertEqual(
            graph_render_module._LGRC9V3_IDENTITY_EDGE,
            graph_render_module._node_edgecolor(
                checkpoint.node_records[0],
                checkpoint=checkpoint,
            ),
        )

    def test_lgrc9v3_visual_bundle_renders_from_lgrc_telemetry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _synthetic_lgrc9v3_run_pack(Path(temp_dir))
            behavior_layout = visualization.build_run_visualization_layout(
                pack.layout,
                visualization_root=Path(temp_dir) / "visualization" / "lgrc9v3",
            )
            graph_layout = visualization.build_graph_run_visualization_layout(
                pack.layout,
                visualization_root=Path(temp_dir) / "visualization" / "lgrc9v3-graph",
            )

            visualization.render_run_visual_bundle(
                pack,
                layout=behavior_layout,
                observables=visualization.DEFAULT_LGRC9V3_RUN_OBSERVABLES,
            )
            visualization.render_graph_run_visual_bundle(pack, layout=graph_layout)

            self.assertTrue(behavior_layout.trajectory_figure_path.exists())
            self.assertTrue(behavior_layout.event_timeline_path.exists())
            self.assertTrue(behavior_layout.report_panel_path.exists())
            self.assertTrue(graph_layout.sequence_figure_path.exists())
            self.assertTrue(graph_layout.final_html_path.exists())
            self.assertTrue(graph_layout.layout_json_path.exists())
            snapshot_paths = sorted(graph_layout.snapshots_dir.glob("*.png"))
            self.assertEqual(2, len(snapshot_paths))

    def test_grc9v3_representative_visual_suite_rejects_disabled_overlays(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _write_synthetic_grc9v3_artifact(
                Path(temp_dir),
                with_graph_checkpoints=True,
                with_checkpoint_overlays=False,
            )

            with self.assertRaisesRegex(ValueError, "enabled checkpoint overlays"):
                visualization.render_grc9v3_representative_visual_suite(
                    telemetry_root=Path(temp_dir) / "outputs",
                    surface_mode=visualization.SURFACE_MODE_GRAPH,
                )

    def test_grc9v3_representative_visual_suite_all_writes_behavior_and_graph_outputs(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _write_synthetic_grc9v3_artifact(Path(temp_dir), with_graph_checkpoints=True)

            result = visualization.render_grc9v3_representative_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                visualization_root=Path(temp_dir) / "visualization",
                surface_mode=visualization.SURFACE_MODE_ALL,
            )

            self.assertTrue(result.visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.visualization_layout.event_timeline_path.exists())
            self.assertTrue(result.visualization_layout.report_panel_path.exists())
            self.assertIsNotNone(result.graph_visualization_layout)
            assert result.graph_visualization_layout is not None
            self.assertTrue(result.graph_visualization_layout.sequence_figure_path.exists())

    def test_grc9_report_lines_include_family_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=3,
            )

            lines = render_module._build_run_report_lines(result.primary_report)

            self.assertTrue(any("family_extensions:" == line for line in lines))
            self.assertTrue(
                any(
                    "grc9.backend_summary.expansion_distribution_mode:" in line
                    for line in lines
                )
            )
            self.assertTrue(
                any(
                    "grc9.expansion_summary.final_expansion_registry_size:" in line
                    for line in lines
                )
            )

    def test_grc9_comparison_report_lines_include_family_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=3,
            )

            lines = render_module._build_comparison_report_lines(result.comparison_report)

            self.assertTrue(any("family_extensions:" == line for line in lines))
            self.assertTrue(any("left.grc9.contract_version:" in line for line in lines))
            self.assertTrue(any("right.grc9.contract_version:" in line for line in lines))

    def test_render_grc9_representative_visual_suite_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=3,
            )
            result = visualization.render_grc9_representative_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
            )

            self.assertEqual("behavior", result.surface_mode)
            self.assertTrue(result.primary_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.primary_visualization_layout.event_timeline_path.exists())
            self.assertTrue(result.primary_visualization_layout.report_panel_path.exists())
            self.assertTrue(result.replay_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.replay_visualization_layout.event_timeline_path.exists())
            self.assertTrue(result.replay_visualization_layout.report_panel_path.exists())
            self.assertTrue(result.comparison_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.comparison_visualization_layout.report_panel_path.exists())
            self.assertIsNone(result.primary_graph_visualization_layout)
            self.assertIsNone(result.replay_graph_visualization_layout)
            self.assertIsNone(result.graph_comparison_visualization_layout)

    def test_render_grc9_representative_visual_suite_rejects_graph_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=3,
            )

            with self.assertRaises(ValueError) as ctx:
                visualization.render_grc9_representative_visual_suite(
                    telemetry_root=Path(temp_dir) / "outputs",
                    surface_mode="graph",
                )

            self.assertIn("record_graph_checkpoints=True", str(ctx.exception))

    def test_render_grc9_representative_visual_suite_writes_graph_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=3,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                include_flow_overlays=True,
            )
            result = visualization.render_grc9_representative_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                surface_mode="graph",
            )

            self.assertEqual("graph", result.surface_mode)
            assert result.primary_graph_visualization_layout is not None
            assert result.replay_graph_visualization_layout is not None
            assert result.graph_comparison_visualization_layout is not None
            self.assertTrue(result.primary_graph_visualization_layout.sequence_figure_path.exists())
            self.assertTrue(result.primary_graph_visualization_layout.final_html_path.exists())
            self.assertTrue(result.replay_graph_visualization_layout.animation_path.exists())
            self.assertTrue(
                result.graph_comparison_visualization_layout.final_comparison_path.exists()
            )

    def test_grc9_landscape_report_lines_include_family_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
            )

            lines = render_module._build_run_report_lines(result.cell1_report)

            self.assertTrue(any("family_extensions:" == line for line in lines))
            self.assertTrue(
                any(
                    "grc9.lane_context.source_lowering_mode:" in line
                    for line in lines
                )
            )
            self.assertTrue(
                any(
                    "grc9.final_identity_summary.sink_count:" in line
                    for line in lines
                )
            )

    def test_grc9_landscape_comparison_report_lines_include_family_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
            )

            lines = render_module._build_comparison_report_lines(result.comparison_report)

            self.assertTrue(any("family_extensions:" == line for line in lines))
            self.assertTrue(any("left.grc9.contract_version:" in line for line in lines))
            self.assertTrue(any("right.grc9.contract_version:" in line for line in lines))

    def test_render_grc9_landscape_visual_suite_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
            )
            result = visualization.render_grc9_landscape_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
            )

            self.assertEqual("behavior", result.surface_mode)
            self.assertTrue(result.cell1_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.cell1_visualization_layout.event_timeline_path.exists())
            self.assertTrue(result.cell1_visualization_layout.report_panel_path.exists())
            self.assertTrue(result.cell4_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.cell4_visualization_layout.event_timeline_path.exists())
            self.assertTrue(result.cell4_visualization_layout.report_panel_path.exists())
            self.assertTrue(result.comparison_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.comparison_visualization_layout.report_panel_path.exists())
            self.assertIsNone(result.cell1_graph_visualization_layout)
            self.assertIsNone(result.cell4_graph_visualization_layout)
            self.assertIsNone(result.graph_comparison_visualization_layout)

    def test_grc9_landscape_visual_labels_do_not_claim_grcl9_lowering(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
            )

            lines = render_module._build_run_report_lines(result.cell1_report)
            joined_lines = "\n".join(lines)

            self.assertIn("structural_graph_graft_v1", joined_lines)
            self.assertNotIn("GRCL-9", joined_lines)

    def test_render_grc9_landscape_visual_suite_rejects_graph_surface_without_checkpoints(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
            )

            with self.assertRaises(ValueError) as ctx:
                visualization.render_grc9_landscape_visual_suite(
                    telemetry_root=Path(temp_dir) / "outputs",
                    surface_mode="graph",
                )

            self.assertIn("record_graph_checkpoints=True", str(ctx.exception))

    def test_render_grc9_landscape_visual_suite_writes_graph_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                include_flow_overlays=True,
            )
            result = visualization.render_grc9_landscape_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                surface_mode="graph",
            )

            self.assertEqual("graph", result.surface_mode)
            assert result.cell1_graph_visualization_layout is not None
            assert result.cell4_graph_visualization_layout is not None
            assert result.graph_comparison_visualization_layout is not None
            self.assertTrue(result.cell1_graph_visualization_layout.sequence_figure_path.exists())
            self.assertTrue(result.cell1_graph_visualization_layout.final_html_path.exists())
            self.assertTrue(result.cell4_graph_visualization_layout.animation_path.exists())
            self.assertTrue(
                result.graph_comparison_visualization_layout.final_comparison_path.exists()
            )

    def test_render_grcv3_representative_visual_suite_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=3,
            )
            result = visualization.render_grcv3_representative_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
            )

            self.assertEqual("behavior", result.surface_mode)
            self.assertTrue(result.primary_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.primary_visualization_layout.event_timeline_path.exists())
            self.assertTrue(result.primary_visualization_layout.report_panel_path.exists())
            self.assertTrue(result.replay_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.comparison_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.comparison_visualization_layout.report_panel_path.exists())

    def test_render_grcv3_representative_visual_suite_writes_graph_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=3,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                include_flow_overlays=True,
            )
            result = visualization.render_grcv3_representative_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                surface_mode="graph",
            )

            self.assertEqual("graph", result.surface_mode)
            assert result.primary_graph_visualization_layout is not None
            assert result.replay_graph_visualization_layout is not None
            assert result.graph_comparison_visualization_layout is not None
            self.assertTrue(result.primary_graph_visualization_layout.sequence_figure_path.exists())
            self.assertTrue(result.primary_graph_visualization_layout.final_html_path.exists())
            self.assertTrue(result.replay_graph_visualization_layout.animation_path.exists())
            self.assertTrue(
                result.graph_comparison_visualization_layout.final_comparison_path.exists()
            )

    def test_render_grcv3_representative_visual_suite_rejects_graph_surface_without_checkpoints(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=3,
            )
            with self.assertRaises(ValueError) as ctx:
                visualization.render_grcv3_representative_visual_suite(
                    telemetry_root=Path(temp_dir) / "outputs",
                    lane_name="phase5_reference",
                    surface_mode="graph",
                )

            self.assertIn("record_graph_checkpoints=True", str(ctx.exception))

    def test_render_grcv3_landscape_visual_suite_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name="seed_baseline",
                num_steps=3,
            )
            result = visualization.render_grcv3_landscape_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name="seed_baseline",
            )

            self.assertEqual("behavior", result.surface_mode)
            self.assertTrue(result.cell1_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.cell1_visualization_layout.event_timeline_path.exists())
            self.assertTrue(result.cell1_visualization_layout.report_panel_path.exists())
            self.assertTrue(result.cell4_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.comparison_visualization_layout.trajectory_figure_path.exists())
            self.assertTrue(result.comparison_visualization_layout.report_panel_path.exists())

    def test_render_grcv3_landscape_visual_suite_rejects_graph_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name="seed_baseline",
                num_steps=3,
            )
            with self.assertRaises(ValueError) as ctx:
                visualization.render_grcv3_landscape_visual_suite(
                    telemetry_root=Path(temp_dir) / "outputs",
                    profile_name="seed_baseline",
                    surface_mode="graph",
                )

            self.assertIn("record_graph_checkpoints=True", str(ctx.exception))

    def test_render_grcv3_landscape_visual_suite_writes_graph_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                telemetry_experiment_path=Path("representative") / "grcv3_landscape_checkpoint",
                profile_name="seed_baseline",
                num_steps=3,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                include_flow_overlays=True,
            )
            result = visualization.render_grcv3_landscape_visual_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                telemetry_experiment_path=Path("representative") / "grcv3_landscape_checkpoint",
                profile_name="seed_baseline",
                surface_mode="graph",
            )

            self.assertEqual("graph", result.surface_mode)
            assert result.cell1_graph_visualization_layout is not None
            assert result.cell4_graph_visualization_layout is not None
            assert result.graph_comparison_visualization_layout is not None
            self.assertTrue(result.cell1_graph_visualization_layout.sequence_figure_path.exists())
            self.assertTrue(result.cell1_graph_visualization_layout.final_html_path.exists())
            self.assertTrue(result.cell4_graph_visualization_layout.animation_path.exists())
            self.assertTrue(
                result.graph_comparison_visualization_layout.final_comparison_path.exists()
            )

    def test_render_representative_graph_suite_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv2_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                num_steps=3,
                family_name="balanced_baseline",
                rng_seed=7,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                checkpoint_storage_mode="jsonl_chunks",
                include_flow_overlays=True,
            )
            result = visualization.render_grcv2_representative_graph_suite(
                telemetry_root=Path(temp_dir) / "outputs",
                family_name="balanced_baseline",
            )

            self.assertTrue(result.cell1_graph_visualization_layout.sequence_figure_path.exists())
            self.assertTrue(result.cell1_graph_visualization_layout.final_html_path.exists())
            self.assertTrue(result.cell1_graph_visualization_layout.animation_path.exists())
            self.assertTrue(result.cell4_graph_visualization_layout.sequence_figure_path.exists())
            self.assertTrue(result.graph_comparison_visualization_layout.final_comparison_path.exists())

    def test_representative_visuals_cli_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv2_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                num_steps=3,
                family_name="balanced_baseline",
                rng_seed=7,
            )
            exit_code = representative_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--family",
                    "balanced_baseline",
                    "--surface",
                    "behavior",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (
                    Path(temp_dir)
                    / "outputs"
                    / "representative"
                    / "grcv2"
                    / "balanced_baseline"
                    / "cell-1"
                    / next(
                        path.name
                        for path in (
                            (
                                Path(temp_dir)
                                / "outputs"
                                / "representative"
                                / "grcv2"
                                / "balanced_baseline"
                                / "cell-1"
                            ).iterdir()
                        )
                        if path.is_dir()
                    )
                    / "visualization"
                ).exists()
            )

    def test_representative_visuals_cli_writes_graph_outputs_when_checkpoints_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv2_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                num_steps=3,
                family_name="balanced_baseline",
                rng_seed=7,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                include_flow_overlays=True,
            )
            exit_code = representative_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--family",
                    "balanced_baseline",
                    "--surface",
                    "graph",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (
                    Path(temp_dir)
                    / "outputs"
                    / "representative"
                    / "grcv2"
                    / "balanced_baseline"
                    / "cell-1"
                    / next(
                        path.name
                        for path in (
                            (
                                Path(temp_dir)
                                / "outputs"
                                / "representative"
                                / "grcv2"
                                / "balanced_baseline"
                                / "cell-1"
                            ).iterdir()
                        )
                        if path.is_dir()
                    )
                    / "visualization"
                    / "graph_animation.gif"
                ).exists()
            )

    def test_representative_visuals_cli_rejects_graph_surface_without_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv2_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                num_steps=3,
                family_name="balanced_baseline",
                rng_seed=7,
            )
            stderr_buffer = io.StringIO()
            with self.assertRaises(SystemExit) as ctx:
                with contextlib.redirect_stderr(stderr_buffer):
                    representative_visuals_main(
                        [
                            "--telemetry-root",
                            str(Path(temp_dir) / "outputs"),
                            "--family",
                            "balanced_baseline",
                            "--surface",
                            "graph",
                        ]
                    )

            self.assertEqual(2, ctx.exception.code)
            self.assertIn("record_graph_checkpoints=True", stderr_buffer.getvalue())

    def test_grcv3_representative_visuals_cli_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=3,
            )
            exit_code = grcv3_representative_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--lane-name",
                    "phase5_reference",
                    "--surface",
                    "behavior",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (
                    Path(temp_dir)
                    / "outputs"
                    / "representative"
                    / "grcv3"
                    / "phase5_reference"
                    / "primary"
                    / next(
                        path.name
                        for path in (
                            (
                                Path(temp_dir)
                                / "outputs"
                                / "representative"
                                / "grcv3"
                                / "phase5_reference"
                                / "primary"
                            ).iterdir()
                        )
                        if path.is_dir()
                    )
                    / "visualization"
                ).exists()
            )

    def test_grcv3_representative_visuals_cli_writes_graph_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=3,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                include_flow_overlays=True,
            )
            exit_code = grcv3_representative_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--lane-name",
                    "phase5_reference",
                    "--surface",
                    "graph",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (
                    Path(temp_dir)
                    / "outputs"
                    / "representative"
                    / "grcv3"
                    / "phase5_reference"
                    / "primary"
                    / next(
                        path.name
                        for path in (
                            (
                                Path(temp_dir)
                                / "outputs"
                                / "representative"
                                / "grcv3"
                                / "phase5_reference"
                                / "primary"
                            ).iterdir()
                        )
                        if path.is_dir()
                    )
                    / "visualization"
                    / "graph_animation.gif"
                ).exists()
            )

    def test_grcv3_representative_visuals_cli_rejects_graph_surface_without_checkpoints(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=3,
            )
            stderr_buffer = io.StringIO()
            with self.assertRaises(SystemExit) as ctx:
                with contextlib.redirect_stderr(stderr_buffer):
                    grcv3_representative_visuals_main(
                        [
                            "--telemetry-root",
                            str(Path(temp_dir) / "outputs"),
                            "--lane-name",
                            "phase5_reference",
                            "--surface",
                            "graph",
                        ]
                    )

            self.assertEqual(2, ctx.exception.code)
            self.assertIn("record_graph_checkpoints=True", stderr_buffer.getvalue())

    def test_grcv3_landscape_visuals_cli_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name="seed_baseline",
                num_steps=3,
            )
            exit_code = grcv3_landscape_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--profile",
                    "seed_baseline",
                    "--surface",
                    "behavior",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (
                    Path(temp_dir)
                    / "outputs"
                    / "representative"
                    / "grcv3_landscape"
                    / "seed_baseline"
                    / "cell-1"
                    / next(
                        path.name
                        for path in (
                            (
                                Path(temp_dir)
                                / "outputs"
                                / "representative"
                                / "grcv3_landscape"
                                / "seed_baseline"
                                / "cell-1"
                            ).iterdir()
                        )
                        if path.is_dir()
                    )
                    / "visualization"
                ).exists()
            )

    def test_grcv3_landscape_visuals_cli_writes_graph_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                telemetry_experiment_path=Path("representative") / "grcv3_landscape_checkpoint",
                profile_name="seed_baseline",
                num_steps=3,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                include_flow_overlays=True,
            )
            exit_code = grcv3_landscape_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--experiment-path",
                    "representative/grcv3_landscape_checkpoint",
                    "--profile",
                    "seed_baseline",
                    "--surface",
                    "graph",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (
                    Path(temp_dir)
                    / "outputs"
                    / "representative"
                    / "grcv3_landscape_checkpoint"
                    / "seed_baseline"
                    / "cell-1"
                    / next(
                        path.name
                        for path in (
                            (
                                Path(temp_dir)
                                / "outputs"
                                / "representative"
                                / "grcv3_landscape_checkpoint"
                                / "seed_baseline"
                                / "cell-1"
                            ).iterdir()
                        )
                        if path.is_dir()
                    )
                    / "visualization"
                    / "graph_animation.gif"
                ).exists()
            )

    def test_grcv3_landscape_visuals_cli_rejects_graph_surface_without_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv3_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name="seed_baseline",
                num_steps=3,
            )
            stderr_buffer = io.StringIO()
            with self.assertRaises(SystemExit) as ctx:
                with contextlib.redirect_stderr(stderr_buffer):
                    grcv3_landscape_visuals_main(
                        [
                            "--telemetry-root",
                            str(Path(temp_dir) / "outputs"),
                            "--profile",
                            "seed_baseline",
                            "--surface",
                            "graph",
                        ]
                    )

            self.assertEqual(2, ctx.exception.code)
            self.assertIn("record_graph_checkpoints=True", stderr_buffer.getvalue())

    def test_grc9_representative_visuals_cli_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=2,
            )
            exit_code = grc9_representative_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--surface",
                    "behavior",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (
                    Path(temp_dir)
                    / "outputs"
                    / "representative"
                    / "grc9"
                    / telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE
                    / "primary"
                    / next(
                        path.name
                        for path in (
                            (
                                Path(temp_dir)
                                / "outputs"
                                / "representative"
                                / "grc9"
                                / telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE
                                / "primary"
                            ).iterdir()
                        )
                        if path.is_dir()
                    )
                    / "visualization"
                    / "trajectories.png"
                ).exists()
            )

    def test_grc9_representative_visuals_cli_writes_graph_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=2,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                include_flow_overlays=True,
            )
            exit_code = grc9_representative_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--surface",
                    "graph",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (
                    Path(temp_dir)
                    / "outputs"
                    / "representative"
                    / "grc9"
                    / telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE
                    / "primary"
                    / next(
                        path.name
                        for path in (
                            (
                                Path(temp_dir)
                                / "outputs"
                                / "representative"
                                / "grc9"
                                / telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE
                                / "primary"
                            ).iterdir()
                        )
                        if path.is_dir()
                    )
                    / "visualization"
                    / "graph_animation.gif"
                ).exists()
            )

    def test_grc9_representative_visuals_cli_rejects_graph_surface_without_checkpoints(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=2,
            )
            stderr_buffer = io.StringIO()
            with self.assertRaises(SystemExit) as ctx:
                with contextlib.redirect_stderr(stderr_buffer):
                    grc9_representative_visuals_main(
                        [
                            "--telemetry-root",
                            str(Path(temp_dir) / "outputs"),
                            "--surface",
                            "graph",
                        ]
                    )

            self.assertEqual(2, ctx.exception.code)
            self.assertIn("record_graph_checkpoints=True", stderr_buffer.getvalue())

    def test_grc9v3_representative_visuals_cli_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _write_synthetic_grc9v3_artifact(Path(temp_dir))
            exit_code = grc9v3_representative_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--surface",
                    "behavior",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue((pack.layout.run_dir / "visualization" / "trajectories.png").exists())

    def test_grc9v3_representative_visuals_cli_writes_graph_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _write_synthetic_grc9v3_artifact(
                Path(temp_dir),
                with_graph_checkpoints=True,
            )
            exit_code = grc9v3_representative_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--surface",
                    "graph",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (pack.layout.run_dir / "visualization" / "graph_animation.gif").exists()
            )

    def test_grc9v3_representative_visuals_cli_rejects_graph_surface_without_checkpoints(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _write_synthetic_grc9v3_artifact(Path(temp_dir))
            stderr_buffer = io.StringIO()
            with self.assertRaises(SystemExit) as ctx:
                with contextlib.redirect_stderr(stderr_buffer):
                    grc9v3_representative_visuals_main(
                        [
                            "--telemetry-root",
                            str(Path(temp_dir) / "outputs"),
                            "--surface",
                            "graph",
                        ]
                    )

            self.assertEqual(2, ctx.exception.code)
            self.assertIn("requires saved graph checkpoints", stderr_buffer.getvalue())

    def test_grc9v3_representative_visuals_cli_accepts_explicit_artifact_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = _write_synthetic_grc9v3_artifact(Path(temp_dir))
            exit_code = grc9v3_representative_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "missing"),
                    "--artifact-path",
                    str(pack.layout.run_dir),
                    "--surface",
                    "behavior",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue((pack.layout.run_dir / "visualization" / "events.png").exists())

    def test_grc9_landscape_visuals_cli_writes_behavior_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
            )
            exit_code = grc9_landscape_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--surface",
                    "behavior",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (
                    Path(temp_dir)
                    / "outputs"
                    / "representative"
                    / "grc9_landscape"
                    / telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE
                    / "cell-1"
                    / next(
                        path.name
                        for path in (
                            (
                                Path(temp_dir)
                                / "outputs"
                                / "representative"
                                / "grc9_landscape"
                                / telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE
                                / "cell-1"
                            ).iterdir()
                        )
                        if path.is_dir()
                    )
                    / "visualization"
                    / "trajectories.png"
                ).exists()
            )

    def test_grc9_landscape_visuals_cli_writes_graph_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                include_flow_overlays=True,
            )
            exit_code = grc9_landscape_visuals_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--surface",
                    "graph",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (
                    Path(temp_dir)
                    / "outputs"
                    / "representative"
                    / "grc9_landscape"
                    / telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE
                    / "cell-1"
                    / next(
                        path.name
                        for path in (
                            (
                                Path(temp_dir)
                                / "outputs"
                                / "representative"
                                / "grc9_landscape"
                                / telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE
                                / "cell-1"
                            ).iterdir()
                        )
                        if path.is_dir()
                    )
                    / "visualization"
                    / "graph_animation.gif"
                ).exists()
            )

    def test_grc9_landscape_visuals_cli_rejects_graph_surface_without_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
            )
            stderr_buffer = io.StringIO()
            with self.assertRaises(SystemExit) as ctx:
                with contextlib.redirect_stderr(stderr_buffer):
                    grc9_landscape_visuals_main(
                        [
                            "--telemetry-root",
                            str(Path(temp_dir) / "outputs"),
                            "--surface",
                            "graph",
                        ]
                    )

            self.assertEqual(2, ctx.exception.code)
            self.assertIn("record_graph_checkpoints=True", stderr_buffer.getvalue())

    def test_representative_graphs_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry.run_grcv2_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                num_steps=3,
                family_name="balanced_baseline",
                rng_seed=7,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                checkpoint_storage_mode="jsonl_chunks",
                include_flow_overlays=True,
            )
            exit_code = representative_graphs_main(
                [
                    "--telemetry-root",
                    str(Path(temp_dir) / "outputs"),
                    "--family",
                    "balanced_baseline",
                ]
            )

            self.assertEqual(0, exit_code)


if __name__ == "__main__":
    unittest.main()
