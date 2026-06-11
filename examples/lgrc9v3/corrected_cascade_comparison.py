"""Reproduce the corrected GRC9V3/LGRC9V3 front-capacity comparison.

What this does:
    Regenerates the corrected 20-step synchronous GRC9V3 baseline when missing,
    then runs a 100-event native LGRC9V3 event-queue comparison from the same
    corrected initial state.

Why it is needed:
    The generated artifacts live under `outputs/`, which is ignored by git.
    This script is the tracked reproduction record for the comparison discussed
    in the LGRC9V3 handoff and reference guide.

Boundary:
    The comparison aligns a corrected source/frontier fixture, not clocks.
    One LGRC queue event is not claimed to equal one synchronous GRC9V3 step.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, is_dataclass, replace
import json
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any

from pygrc.models import (
    GRC9V3,
    LGRC9V3,
    LGRC9V3CorrectedCascadeScenarioPolicy,
    build_lgrc9v3_corrected_cascade_runtime,
    prime_lgrc9v3_corrected_cascade_broad_seed,
    prime_lgrc9v3_corrected_cascade_queues,
)
from pygrc.telemetry import (
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    TelemetryArtifactLayout,
    TelemetryArtifactPack,
    build_lgrc9v3_graph_checkpoint,
    build_telemetry_artifact_layout,
    event_rows_from_events,
    lgrc9v3_event_family_extensions_for_events,
    lgrc9v3_run_summary_family_extensions,
    lgrc9v3_step_family_extensions,
    load_telemetry_artifact_pack,
    run_summary_from_step_results,
    save_telemetry_artifact_pack,
    step_row_from_step_result,
)
from pygrc.visualization import (
    build_graph_comparison_visualization_layout,
    build_graph_run_visualization_layout,
    render_graph_comparison_visual_bundle,
    render_graph_run_visual_bundle,
)


ROOT = Path(__file__).resolve().parents[2]
GRC_SESSION_ID = "S_LGRC_COMPARE_CORRECTED"
GRC_RUN_ID = "appendix_e_cell_division_corrected_full_capacity_cascade"
GRC_RUN_DIR = (
    ROOT
    / f"outputs/grcl9v3/lowering/sessions/{GRC_SESSION_ID}/lanes"
    / GRC_RUN_ID
)
INITIAL_SNAPSHOT = GRC_RUN_DIR / "snapshots/initial_snapshot.json"
FINAL_SNAPSHOT = GRC_RUN_DIR / "snapshots/final_snapshot.json"
OUTPUT_ROOT = ROOT / "outputs/examples/lgrc9v3_corrected_comparison"
LGRC_RUN_ID = "lgrc9v3_corrected_cascade_100_events"
CORRECTED_POLICY = LGRC9V3CorrectedCascadeScenarioPolicy()


def ensure_corrected_grc_baseline() -> None:
    """Regenerate the ignored corrected GRC9V3 baseline if it is absent."""

    required_paths = (
        INITIAL_SNAPSHOT,
        FINAL_SNAPSHOT,
        GRC_RUN_DIR / "telemetry/events.jsonl",
        GRC_RUN_DIR / "telemetry/graph_checkpoints/index.json",
    )
    if all(path.exists() for path in required_paths):
        return
    command = [
        sys.executable,
        "-m",
        "pygrc.telemetry.grcl9v3_replay",
        "--session-id",
        GRC_SESSION_ID,
        "--steps",
        "20",
        "--source-mode",
        "landscape_seed_examples",
        "--fixture",
        GRC_RUN_ID,
    ]
    print("Regenerating corrected GRC9V3 baseline:")
    print(" ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def plain(value: Any) -> Any:
    """Return a JSON-compatible value."""

    if is_dataclass(value):
        return plain(asdict(value))
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if hasattr(value, "to_record"):
        return plain(value.to_record())
    if hasattr(value, "to_artifact"):
        return plain(value.to_artifact())
    return value


def checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[Any, ...],
) -> GraphCheckpointIndex:
    """Build a file-backed graph checkpoint index."""

    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="initial+every_event",
        selection_params={"include_initial": True, "include_each_event": True},
        checkpoints=tuple(
            GraphCheckpointReference(
                checkpoint_id=checkpoint.checkpoint_id,
                step_index=checkpoint.step_index,
                time=checkpoint.time,
                checkpoint_label=checkpoint.checkpoint_label,
                checkpoint_reason=checkpoint.checkpoint_reason,
                path=f"{checkpoint.checkpoint_id}.json",
                event_step_range=checkpoint.event_step_range,
                event_count_window=checkpoint.event_count_window,
                event_counts_by_kind_window=checkpoint.event_counts_by_kind_window,
            )
            for checkpoint in checkpoints
        ),
    )


def event_window_counts(events: list[Any]) -> dict[str, int]:
    return dict(Counter(event.kind for event in events))


def sanitize_graph_checkpoint(checkpoint: Any) -> Any:
    """Replace optional numeric edge-label `None` values for graph rendering."""

    numeric_edge_keys = {
        "base_conductance",
        "conductance",
        "geometric_length",
        "temporal_delay",
        "flux_coupling",
        "flux",
        "flux_uv",
    }
    edge_records: list[dict[str, Any]] = []
    for record in checkpoint.edge_records:
        updated = dict(record)
        for key in numeric_edge_keys:
            if updated.get(key) is None:
                updated[key] = 0.0
        edge_records.append(updated)
    return replace(checkpoint, edge_records=tuple(edge_records))


def sanitize_pack(pack: TelemetryArtifactPack) -> TelemetryArtifactPack:
    """Return a pack whose graph checkpoints are render-safe."""

    return replace(
        pack,
        graph_checkpoints=tuple(
            sanitize_graph_checkpoint(checkpoint)
            for checkpoint in pack.graph_checkpoints
        ),
    )


def render_graph_bundle_tolerant(
    pack: TelemetryArtifactPack,
    *,
    layout: Any,
) -> str | None:
    """Render graph bundle, but keep comparison artifacts if HTML lineage fails."""

    try:
        render_graph_run_visual_bundle(pack, layout=layout)
    except Exception as exc:  # noqa: BLE001 - output script should preserve run artifacts.
        return f"{type(exc).__name__}: {exc}"
    return None


def touched_nodes(events: list[Any]) -> dict[str, Any]:
    """Collect event payload node references for activity-spread comparison."""

    nodes_by_kind: dict[str, set[int]] = defaultdict(set)
    keys = {
        "node_id",
        "node_ids",
        "source_node_id",
        "target_node_id",
        "parent_node_id",
        "child_node_id",
        "candidate_node_id",
        "sink_node_id",
        "trigger_node_id",
        "target_node_ids",
        "module_node_ids",
        "stabilized_child_node_ids",
        "transferred_node_ids",
        "competing_sink_ids",
        "selected_sink_id",
        "losing_sink_ids",
    }

    def collect(kind: str, item: Any) -> None:
        if isinstance(item, dict):
            for key, nested in item.items():
                if (
                    key in keys
                    or key.endswith("node_id")
                    or key.endswith("node_ids")
                    or key.endswith("sink_id")
                    or key.endswith("sink_ids")
                ):
                    collect(kind, nested)
                elif isinstance(nested, (dict, list, tuple)):
                    collect(kind, nested)
        elif isinstance(item, (list, tuple)):
            for nested in item:
                collect(kind, nested)
        elif not isinstance(item, bool):
            try:
                value = int(item)
            except (TypeError, ValueError):
                return
            if value >= 0:
                nodes_by_kind[kind].add(value)

    for event in events:
        collect(event.kind, dict(event.payload))
    all_nodes = sorted(set().union(*nodes_by_kind.values()) if nodes_by_kind else set())
    return {
        "distinct_touched_node_count": len(all_nodes),
        "distinct_touched_nodes": all_nodes,
        "touched_node_count_by_kind": {
            kind: len(nodes) for kind, nodes in sorted(nodes_by_kind.items())
        },
    }


def proper_time_surface_summary(model: LGRC9V3) -> dict[str, Any]:
    """Summarize final live-node local proper-time differences."""

    state = model.get_state()
    live_node_ids = tuple(sorted(state.base_state.topology.iter_live_node_ids()))
    values = {
        int(node_id): float(state.node_proper_time.get(int(node_id), 0.0))
        for node_id in live_node_ids
    }
    last_event_keys = {
        int(node_id): float(state.node_last_update_event_time_key.get(int(node_id), 0.0))
        for node_id in live_node_ids
    }
    if not values:
        return {
            "live_node_count": 0,
            "min_tau": 0.0,
            "max_tau": 0.0,
            "range_tau": 0.0,
            "mean_tau": 0.0,
            "median_tau": 0.0,
            "top_tau_nodes": [],
            "bottom_tau_nodes": [],
            "removed_or_lineage_clock_nodes": {},
        }
    sorted_items = sorted(values.items(), key=lambda item: (-item[1], item[0]))
    bottom_items = sorted(values.items(), key=lambda item: (item[1], item[0]))
    removed_or_lineage = {
        int(node_id): float(tau)
        for node_id, tau in sorted(state.node_proper_time.items())
        if int(node_id) not in values
    }
    return {
        "live_node_count": len(values),
        "min_tau": min(values.values()),
        "max_tau": max(values.values()),
        "range_tau": max(values.values()) - min(values.values()),
        "mean_tau": statistics.mean(values.values()),
        "median_tau": statistics.median(values.values()),
        "top_tau_nodes": [
            {
                "node_id": node_id,
                "tau_i": tau,
                "last_event_time_key": last_event_keys[node_id],
            }
            for node_id, tau in sorted_items[:10]
        ],
        "bottom_tau_nodes": [
            {
                "node_id": node_id,
                "tau_i": tau,
                "last_event_time_key": last_event_keys[node_id],
            }
            for node_id, tau in bottom_items[:10]
        ],
        "removed_or_lineage_clock_nodes": removed_or_lineage,
        "interpretation": (
            "With unit lapse in this run, tau_i equals the local clock's last "
            "event-time update. Differences therefore indicate causal queue "
            "activity locality, not non-unit lapse dilation."
        ),
    }


def prepare_lgrc_model() -> LGRC9V3:
    """Create LGRC9V3 through the library-owned corrected-cascade facade."""

    base = GRC9V3.load(str(INITIAL_SNAPSHOT))
    return build_lgrc9v3_corrected_cascade_runtime(
        base,
        policy=CORRECTED_POLICY,
    )


def run_lgrc() -> dict[str, Any]:
    """Run 100 native LGRC9V3 queue events and save artifacts."""

    model = prepare_lgrc_model()
    identity = RunTelemetryIdentity(
        run_id=LGRC_RUN_ID,
        model_family="LGRC9V3",
        params_identity=model.get_params().params_hash,
        seed_name=GRC_RUN_ID,
        seed_source_reference="outputs/grcl9v3/lowering/sessions/S_LGRC_COMPARE_CORRECTED",
        seed_path=str(INITIAL_SNAPSHOT.relative_to(ROOT)),
        param_family="lgrc9v3_corrected_front_capacity_comparison",
        requested_steps=100,
    )
    layout = build_telemetry_artifact_layout(LGRC_RUN_ID, root_dir=OUTPUT_ROOT)
    initial_observables = dict(model.compute_observables())
    checkpoints: list[Any] = [
        sanitize_graph_checkpoint(
            build_lgrc9v3_graph_checkpoint(
                model,
                identity=identity,
                checkpoint_id="checkpoint-00000000",
                checkpoint_label="initial",
                checkpoint_reason="corrected_initial_prepared_diagnostics",
            )
        )
    ]
    prime_lgrc9v3_corrected_cascade_queues(model, policy=CORRECTED_POLICY)

    step_results: list[Any] = []
    step_extensions: list[dict[str, Any]] = []
    all_events: list[Any] = []
    seed_packet_summary: dict[str, Any] = {}
    broad_packets_scheduled = 0
    for event_number in range(1, 101):
        state = model.get_state()
        if (
            event_number > 3
            and broad_packets_scheduled == 0
            and not state.packet_ledger.event_queue_records
            and not state.boundary_birth_trial_queue
        ):
            broad_seed = prime_lgrc9v3_corrected_cascade_broad_seed(
                model,
                policy=CORRECTED_POLICY,
            )
            broad_packets_scheduled = broad_seed.scheduled_count
            seed_packet_summary = broad_seed.to_summary()
        if (
            not model.get_state().packet_ledger.event_queue_records
            and not model.get_state().boundary_birth_trial_queue
        ):
            break
        result = model.step()
        step_results.append(result)
        step_extensions.append(lgrc9v3_step_family_extensions(model))
        events = list(result.events)
        all_events.extend(events)
        checkpoints.append(
            sanitize_graph_checkpoint(
                build_lgrc9v3_graph_checkpoint(
                    model,
                    identity=identity,
                    checkpoint_id=f"checkpoint-{event_number:08d}",
                    checkpoint_label=f"event_{event_number:03d}",
                    checkpoint_reason=str(
                        result.bookkeeping.get("processed_event_kind", "event")
                    ),
                    event_count_window=len(events),
                    event_counts_by_kind_window=event_window_counts(events),
                ),
            )
        )

    step_rows = tuple(
        step_row_from_step_result(
            result,
            identity=identity,
            family_extensions=extension,
        )
        for result, extension in zip(step_results, step_extensions, strict=True)
    )
    event_rows = event_rows_from_events(
        tuple(all_events),
        identity=identity,
        family_extensions_by_event=lgrc9v3_event_family_extensions_for_events(
            tuple(all_events)
        ),
    )
    summary = run_summary_from_step_results(
        tuple(step_results),
        identity=identity,
        initial_observables=initial_observables,
        final_observables=model.compute_observables(),
        resolved_params=model.get_params().resolved_config,
        raw_params=model.get_params().raw_config,
        parameter_overrides={
            "comparison_source": "corrected_front_capacity_cascade",
            "diagnostic_preparation": (
                "grc9v3_rebuild_differential_transport_identity_only"
            ),
            "broad_seed_packets_scheduled": broad_packets_scheduled,
            "seed_packet_max_amount": CORRECTED_POLICY.broad_seed_policy.max_amount,
            "seed_packet_source_fraction": (
                CORRECTED_POLICY.broad_seed_policy.source_fraction
            ),
            "route_total_forward_fraction": (
                CORRECTED_POLICY.route_total_forward_fraction
            ),
        },
        family_extensions=lgrc9v3_run_summary_family_extensions(model),
    )
    graph_index = checkpoint_index(identity, tuple(checkpoints))
    save_telemetry_artifact_pack(
        layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=summary,
        graph_checkpoint_index=graph_index,
        graph_checkpoints=tuple(checkpoints),
    )
    pack = sanitize_pack(TelemetryArtifactPack(
        layout=layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=summary,
        graph_checkpoint_index=graph_index,
        graph_checkpoints=tuple(checkpoints),
    ))
    visual_layout = build_graph_run_visualization_layout(
        layout,
        visualization_root=OUTPUT_ROOT / "visuals",
    )
    visual_warning = render_graph_bundle_tolerant(pack, layout=visual_layout)
    return {
        "run_id": LGRC_RUN_ID,
        "telemetry_dir": str(layout.telemetry_dir.relative_to(ROOT)),
        "visualization_dir": str(visual_layout.run_dir.relative_to(ROOT)),
        "graph_sequence_figure": str(
            visual_layout.sequence_figure_path.relative_to(ROOT)
        ),
        "graph_animation": (
            str(visual_layout.animation_path.relative_to(ROOT))
            if visual_layout.animation_path.exists()
            else None
        ),
        "graph_html": (
            str(visual_layout.final_html_path.relative_to(ROOT))
            if visual_layout.final_html_path.exists()
            else None
        ),
        "visualization_warning": visual_warning,
        "processed_step_results": len(step_results),
        "runtime_event_rows": len(all_events),
        "event_counts_by_kind": dict(Counter(event.kind for event in all_events)),
        "broad_seed_packets_scheduled": broad_packets_scheduled,
        "seed_packet_summary": seed_packet_summary,
        "route_total_forward_fraction": CORRECTED_POLICY.route_total_forward_fraction,
        "final_observables": plain(model.compute_observables()),
        "final_node_count": len(
            tuple(model.get_state().base_state.topology.iter_live_node_ids())
        ),
        "final_edge_count": len(
            tuple(model.get_state().base_state.topology.iter_live_edge_ids())
        ),
        "event_activity": touched_nodes(all_events),
        "proper_time_surface": proper_time_surface_summary(model),
        "max_abs_packet_budget_error": max(
            [
                abs(float(event.payload.get("budget_error", 0.0)))
                for event in all_events
                if "budget_error" in event.payload
            ]
            or [0.0]
        ),
        "boundary_birth_status": model.get_state().base_state.cached_quantities.get(
            "last_causal_boundary_birth_status"
        ),
        "diagnostic_preparation_note": (
            "Initial substrate labels were refreshed with GRC9V3 "
            "diagnostic/transport/identity rebuild helpers only. "
            "Synchronous GRC9V3.step() was not run in the LGRC runtime."
        ),
    }


def load_grc_baseline_metrics() -> tuple[dict[str, Any], Any, Any]:
    """Load and render the corrected 20-step synchronous GRC9V3 baseline."""

    grc_layout = TelemetryArtifactLayout(
        root_dir=GRC_RUN_DIR.parent,
        run_id=GRC_RUN_ID,
        run_dir=GRC_RUN_DIR,
        telemetry_dir=GRC_RUN_DIR / "telemetry",
        step_rows_path=GRC_RUN_DIR / "telemetry/steps.jsonl",
        event_rows_path=GRC_RUN_DIR / "telemetry/events.jsonl",
        run_summary_path=GRC_RUN_DIR / "telemetry/run_summary.json",
        comparison_report_path=GRC_RUN_DIR / "telemetry/comparison_report.json",
        experiment_report_path=GRC_RUN_DIR / "telemetry/experiment_report.json",
        graph_checkpoints_dir=GRC_RUN_DIR / "telemetry/graph_checkpoints",
        graph_checkpoint_index_path=(
            GRC_RUN_DIR / "telemetry/graph_checkpoints/index.json"
        ),
    )
    pack = sanitize_pack(load_telemetry_artifact_pack(grc_layout))
    visual_layout = build_graph_run_visualization_layout(
        grc_layout,
        visualization_root=OUTPUT_ROOT / "visuals",
    )
    visual_warning = render_graph_bundle_tolerant(pack, layout=visual_layout)
    final_model = GRC9V3.load(str(FINAL_SNAPSHOT))
    event_kinds: list[str] = []
    pseudo_events: list[Any] = []
    for row in pack.event_rows:
        kind = str(getattr(row, "event_kind", None) or getattr(row, "kind", None))
        event_kinds.append(kind)
        payload = getattr(row, "payload", {})
        pseudo_events.append(type("EventLike", (), {"kind": kind, "payload": payload})())
    metrics = {
        "run_id": GRC_RUN_ID,
        "telemetry_dir": str(grc_layout.telemetry_dir.relative_to(ROOT)),
        "visualization_dir": str(visual_layout.run_dir.relative_to(ROOT)),
        "graph_sequence_figure": str(
            visual_layout.sequence_figure_path.relative_to(ROOT)
        ),
        "graph_animation": (
            str(visual_layout.animation_path.relative_to(ROOT))
            if visual_layout.animation_path.exists()
            else None
        ),
        "graph_html": (
            str(visual_layout.final_html_path.relative_to(ROOT))
            if visual_layout.final_html_path.exists()
            else None
        ),
        "visualization_warning": visual_warning,
        "step_rows": len(pack.step_rows),
        "event_rows": len(pack.event_rows),
        "event_counts_by_kind": dict(Counter(event_kinds)),
        "final_node_count": len(tuple(final_model.get_state().topology.iter_live_node_ids())),
        "final_edge_count": len(tuple(final_model.get_state().topology.iter_live_edge_ids())),
        "final_observables": plain(final_model.compute_observables()),
        "event_activity": touched_nodes(pseudo_events),
    }
    return metrics, pack, grc_layout


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    ensure_corrected_grc_baseline()
    lgrc_report = run_lgrc()
    grc_metrics, grc_pack, grc_layout = load_grc_baseline_metrics()
    lgrc_layout = build_telemetry_artifact_layout(LGRC_RUN_ID, root_dir=OUTPUT_ROOT)
    lgrc_pack = sanitize_pack(load_telemetry_artifact_pack(lgrc_layout))
    comparison_layout = build_graph_comparison_visualization_layout(
        grc_layout,
        lgrc_layout,
        visualization_root=OUTPUT_ROOT / "visuals",
    )
    comparison_visual_warning = None
    try:
        render_graph_comparison_visual_bundle(
            grc_pack,
            lgrc_pack,
            layout=comparison_layout,
        )
    except Exception as exc:  # noqa: BLE001 - record visualization limitation.
        comparison_visual_warning = f"{type(exc).__name__}: {exc}"
    comparison = {
        "classification": (
            "corrected_front_capacity_grc9v3_vs_lgrc9v3_event_queue_comparison"
        ),
        "source_correction": {
            "corrected_fixture": GRC_RUN_ID,
            "legacy_growth_locus_ids": [],
            "growth_semantics": "front_capacity",
            "legacy_s0022_comparison_rejected_reason": (
                "legacy_birth_inflated_grc9v3_baseline"
            ),
        },
        "comparison_boundary": (
            "GRC9V3 is 20 synchronous steps. LGRC9V3 is 100 native event-queue "
            "steps from the same corrected initial state after diagnostic-label "
            "preparation. This is a corrected source/frontier activity "
            "comparison, not proof that one LGRC event equals one GRC step."
        ),
        "grc9v3_corrected_baseline": grc_metrics,
        "lgrc9v3_corrected_event_queue": lgrc_report,
        "graph_comparison_figure": str(
            comparison_layout.final_comparison_path.relative_to(ROOT)
        ),
        "graph_comparison_visualization_warning": comparison_visual_warning,
        "topology_delta": {
            "grc_final_nodes": grc_metrics["final_node_count"],
            "lgrc_final_nodes": lgrc_report["final_node_count"],
            "grc_final_edges": grc_metrics["final_edge_count"],
            "lgrc_final_edges": lgrc_report["final_edge_count"],
        },
        "activity_delta": {
            "grc_distinct_touched_nodes": grc_metrics["event_activity"][
                "distinct_touched_node_count"
            ],
            "lgrc_distinct_touched_nodes": lgrc_report["event_activity"][
                "distinct_touched_node_count"
            ],
        },
    }
    (OUTPUT_ROOT / "comparison_report.json").write_text(
        json.dumps(plain(comparison), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    summary = f"""# Corrected GRC9V3 / LGRC9V3 Comparison

Classification: `{comparison['classification']}`

This replaces the earlier S0022 comparison that used legacy/aggressive birth
semantics. The corrected source is the front-capacity cascade fixture with no
legacy growth loci.

## Boundary

{comparison['comparison_boundary']}

## GRC9V3 Corrected Baseline

- telemetry: `{grc_metrics['telemetry_dir']}`
- visual sequence: `{grc_metrics['graph_sequence_figure']}`
- final graph HTML: `{grc_metrics['graph_html']}`
- steps: `{grc_metrics['step_rows']}`
- event rows: `{grc_metrics['event_rows']}`
- final topology: `{grc_metrics['final_node_count']}` nodes / `{grc_metrics['final_edge_count']}` edges
- event counts: `{json.dumps(grc_metrics['event_counts_by_kind'], sort_keys=True)}`

## LGRC9V3 Event Queue Run

- telemetry: `{lgrc_report['telemetry_dir']}`
- visual sequence: `{lgrc_report['graph_sequence_figure']}`
- animation: `{lgrc_report['graph_animation']}`
- final graph HTML: `{lgrc_report['graph_html']}`
- processed queue steps: `{lgrc_report['processed_step_results']}`
- runtime event rows: `{lgrc_report['runtime_event_rows']}`
- broad seed packets scheduled: `{lgrc_report['broad_seed_packets_scheduled']}`
- seed packet summary: `{json.dumps(lgrc_report['seed_packet_summary'], sort_keys=True)}`
- route total forward fraction: `{lgrc_report['route_total_forward_fraction']}`
- final topology: `{lgrc_report['final_node_count']}` nodes / `{lgrc_report['final_edge_count']}` edges
- proper-time range across live nodes: `{lgrc_report['proper_time_surface']['range_tau']}`
- proper-time median across live nodes: `{lgrc_report['proper_time_surface']['median_tau']}`
- max packet budget error: `{lgrc_report['max_abs_packet_budget_error']}`
- event counts: `{json.dumps(lgrc_report['event_counts_by_kind'], sort_keys=True)}`

## Activity Spread

- GRC touched nodes: `{grc_metrics['event_activity']['distinct_touched_node_count']}`
- LGRC touched nodes: `{lgrc_report['event_activity']['distinct_touched_node_count']}`
- graph comparison: `{comparison['graph_comparison_figure']}`

## Interpretation

The corrected comparison no longer uses the legacy exponential-birth baseline.
Both sides start from the corrected front-capacity fixture. LGRC reproduces the
same first topological surfaces under its native queue: a causally wrapped
spark candidate, mechanical expansion, proper-time inheritance, and one
explicit front-capacity boundary birth. The later LGRC packet wave is
coherence-aware and broad, so the visual no longer concentrates activity on
only a few nodes while still respecting source-debit conservation.
"""
    (OUTPUT_ROOT / "comparison_summary.md").write_text(summary, encoding="utf-8")
    print(json.dumps(plain(comparison), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
