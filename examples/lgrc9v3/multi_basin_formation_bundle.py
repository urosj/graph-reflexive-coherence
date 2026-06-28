"""Capture and visualize the LGRC9V3 multi-basin formation surface.

What this example does:
    Runs the opt-in native LGRC9V3 multi-basin formation path through route
    arbitration, post-refinement flow-window emission, child-basin extraction,
    replay validation, and fail-closed merge/leakage controls. It saves
    telemetry rows and graph checkpoints under `outputs/examples/lgrc9v3/`,
    then renders graph visuals from those saved checkpoint artifacts.

What this example is not:
    It is not a Phase 8 closeout, not native support evidence, not semantic
    learning, and not agency. The strongest demonstrated ceiling is an MB5
    control-backed native multi-basin formation candidate. MB6 remains false.

Geometry note:
    This specific fixture is not a visible node-birth example. It starts with
    three graph nodes and ends with three graph nodes. Its topology-history
    records are collapse/reabsorption and packet-transport records over the
    existing graph, both with `topology_mutated=false`. The child-basin record
    is intentionally narrow: one core, with the full compact fixture assigned
    to that core. Use `topology_birth_refinement_visual_bundle.py` when you
    want to inspect a checkpoint sequence where node/basin structure visibly
    changes through boundary birth and refinement.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import json
from pathlib import Path

from pygrc.core import PortGraphBackend
from pygrc.models import (
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3NodeState,
    GRC9V3State,
    LAPSE_POLICY_UNIT,
    LGRC_RUNTIME_LEVEL_LGRC3,
    LGRC9V3,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_POST_REFINEMENT_REPLAY,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES,
    LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
    LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE,
    PortEdge,
)
from pygrc.telemetry import (
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    TelemetryArtifactPack,
    build_lgrc9v3_graph_checkpoint,
    build_telemetry_artifact_layout,
    event_rows_from_events,
    lgrc9v3_event_family_extensions_for_events,
    lgrc9v3_run_summary_family_extensions,
    lgrc9v3_step_family_extensions,
    run_summary_from_step_results,
    save_telemetry_artifact_pack,
    step_row_from_step_result,
)
from pygrc.visualization import (
    build_graph_run_visualization_layout,
    render_graph_run_visual_bundle,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_OUTPUT_ROOT = REPO_ROOT / "outputs" / "examples" / "lgrc9v3"
RUN_ID = "lgrc9v3-multi-basin-formation-bundle"


def print_json(label: str, payload: object) -> None:
    """Print deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(jsonable(payload), indent=2, sort_keys=True))


def jsonable(payload: object) -> object:
    """Return a JSON-serializable copy of nested telemetry payloads."""

    if isinstance(payload, Mapping):
        return {str(key): jsonable(value) for key, value in payload.items()}
    if isinstance(payload, Sequence) and not isinstance(payload, str | bytes):
        return [jsonable(value) for value in payload]
    return payload


def display_path(path: Path) -> str:
    """Return a repo-relative path when the artifact lives in this checkout."""

    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def three_node_state() -> GRC9V3State:
    """Return the compact route-arbitration fixture used by this example."""

    graph = PortGraphBackend()
    node_0 = graph.add_node({"label": "source"})
    node_1 = graph.add_node({"label": "middle"})
    node_2 = graph.add_node({"label": "target"})
    edge_01 = graph.connect_ports(node_0, 0, node_1, 0, {"kind": "01"})
    edge_12 = graph.connect_ports(node_1, 1, node_2, 0, {"kind": "12"})
    edge_02 = graph.connect_ports(node_0, 1, node_2, 1, {"kind": "02"})
    return GRC9V3State(
        topology=graph,
        nodes={
            node_0: GRC9V3NodeState(coherence=1.0),
            node_1: GRC9V3NodeState(coherence=2.0),
            node_2: GRC9V3NodeState(coherence=3.0),
        },
        port_edges={
            edge_01: PortEdge(node_0, 1, node_1, 1, conductance=1.0, flux_uv=0.0),
            edge_12: PortEdge(node_1, 2, node_2, 1, conductance=1.0, flux_uv=0.0),
            edge_02: PortEdge(node_0, 2, node_2, 2, conductance=1.0, flux_uv=0.0),
        },
        base_conductance={edge_01: 1.0, edge_12: 1.0, edge_02: 1.0},
        geometric_length={edge_01: 1.0, edge_12: 1.0, edge_02: 1.0},
        temporal_delay={edge_01: 1.0, edge_12: 1.0, edge_02: 1.0},
        flux_coupling={edge_01: 0.0, edge_12: 0.0, edge_02: 0.0},
    )


def multi_basin_params() -> dict[str, object]:
    """Return default-off-compatible params with only required policies enabled."""

    return {
        "dt": 1.0,
        "causal_modes": {
            "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": "explicit_event_time_key",
            "proper_time_accumulation_policy": "local_event_frontier",
            "causal_topology_integration_allowed": True,
            "causal_spark_expansion_allowed": True,
            "causal_refinement_packet_transport_allowed": True,
            "causal_proper_time_inheritance_allowed": True,
            "causal_collapse_reabsorption_allowed": True,
            "causal_identity_acceptance_allowed": False,
            "causal_pulse_substrate_surface_enabled": True,
            "causal_pulse_substrate_surface_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
            ),
            "causal_pulse_substrate_surface_validated": True,
            "causal_pulse_substrate_surface_lineage_transport_enabled": True,
            "causal_pulse_substrate_surface_lineage_transport_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
            ),
            "causal_pulse_substrate_surface_lineage_transport_validated": True,
            "causal_pulse_substrate_surface_lineage_transport_supported": True,
            "causal_topology_state_reabsorption_enabled": True,
            "causal_topology_state_reabsorption_policy": (
                LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
            ),
            "causal_topology_state_reabsorption_validated": True,
            "causal_topology_state_reabsorption_supported": True,
            "native_lgrc_route_arbitration_enabled": True,
            "native_lgrc_route_arbitration_policy": (
                LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
            ),
            "native_lgrc_multi_basin_formation_enabled": True,
            "native_lgrc_multi_basin_formation_policy": (
                LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_POST_REFINEMENT_REPLAY
            ),
            "native_lgrc_multi_basin_formation_validated": False,
            "native_lgrc_multi_basin_formation_supported": False,
        },
    }


def native_route_candidate_spec(
    *,
    candidate_route_id: str,
    selected_sink_id: int,
    losing_sink_ids: tuple[int, ...],
    score: float,
) -> dict[str, object]:
    """Return a serialized, runtime-visible native-route candidate."""

    return {
        "candidate_route_id": candidate_route_id,
        "route_intent": LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
        "candidate_topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        "candidate_competing_sink_ids": (0, 2),
        "candidate_losing_sink_ids": losing_sink_ids,
        "candidate_selected_sink_id": selected_sink_id,
        "candidate_transferred_node_ids": (1, 2),
        "candidate_lineage_transfer_map": {
            1: str(selected_sink_id),
            2: str(selected_sink_id),
        },
        "candidate_source_node_ids": (1, 2),
        "candidate_target_node_ids": (selected_sink_id,),
        "candidate_retired_node_ids": losing_sink_ids,
        "candidate_source_edge_ids": (1,),
        "candidate_target_edge_ids": (0,),
        "candidate_retired_edge_ids": (1,),
        "candidate_route_score": score,
        "candidate_score_components": {"surface_pulse_contact": score},
        "candidate_budget_prediction": {
            "node_plus_packet_budget_before": 6.0,
            "node_plus_packet_budget_after": 6.0,
            "node_plus_packet_budget_error": 0.0,
        },
        "candidate_order_key": candidate_route_id,
        "candidate_runtime_visible_inputs": (
            "candidate_source_surface_digest",
            "surface_pulse_contact",
            "serialized_route_arbitration_policy",
        ),
    }


def checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[object, ...],
) -> GraphCheckpointIndex:
    """Build a file-backed checkpoint index for saved telemetry artifacts."""

    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="initial+after-multi-basin-controls",
        selection_params={
            "include_initial": True,
            "include_after_multi_basin_controls": True,
        },
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


def run_multi_basin_formation_bundle(
    *,
    output_root: Path = EXAMPLE_OUTPUT_ROOT,
) -> dict[str, object]:
    """Run, save, and visualize the multi-basin formation telemetry bundle."""

    model = LGRC9V3.from_state(three_node_state(), multi_basin_params())
    identity = RunTelemetryIdentity(
        run_id=RUN_ID,
        model_family="LGRC9V3",
        params_identity=model.get_params().params_hash,
        seed_name="three-node-multi-basin-fixture",
        seed_source_reference="examples/lgrc9v3/multi_basin_formation_bundle.py",
        seed_path="examples/lgrc9v3/multi_basin_formation_bundle.py",
        param_family="lgrc9v3_native_multi_basin_formation",
        requested_steps=1,
    )
    layout = build_telemetry_artifact_layout(RUN_ID, root_dir=output_root)
    initial_observables = dict(model.compute_observables())
    initial_checkpoint = build_lgrc9v3_graph_checkpoint(
        model,
        identity=identity,
        checkpoint_id="checkpoint-00000000",
        checkpoint_label="initial",
        checkpoint_reason="initial",
    )

    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    step_result = model.step()
    surface = model.get_state().causal_pulse_substrate_surface_log[-1]
    candidate_result = model.emit_native_route_candidate_set(
        arbitration_window_id="window:multi-basin-example",
        source_surface_digest=str(surface.surface_digest),
        unresolved_tie_policy=LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
        candidate_routes=(
            native_route_candidate_spec(
                candidate_route_id="candidate:low",
                selected_sink_id=2,
                losing_sink_ids=(0,),
                score=0.25,
            ),
            native_route_candidate_spec(
                candidate_route_id="candidate:high",
                selected_sink_id=0,
                losing_sink_ids=(2,),
                score=0.75,
            ),
        ),
    )
    candidate_set = candidate_result["candidate_set_record"]
    arbitration = model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
    )["route_arbitration_record"]
    commit = model.commit_native_route_arbitration_selection(
        native_route_arbitration_reference=str(arbitration.native_route_arbitration_digest),
    )
    child = commit["child_basin_state_records"][0]
    replay = model.validate_multi_basin_child_basin_replay(
        source_child_basin_state_digest=str(child.child_basin_state_digest),
        snapshot_replay_artifact=model.snapshot(),
    )
    model.validate_multi_basin_merge_leakage_controls(
        source_child_basin_state_digest=str(child.child_basin_state_digest),
        replay_validation_digest=str(replay["replay_validation_digest"]),
    )

    all_events = tuple(step_result.events)
    event_counts = dict(Counter(event.kind for event in all_events))
    final_checkpoint = build_lgrc9v3_graph_checkpoint(
        model,
        identity=identity,
        checkpoint_id="checkpoint-00000001",
        checkpoint_label="after_multi_basin_controls",
        checkpoint_reason="final",
        event_count_window=len(all_events),
        event_counts_by_kind_window=event_counts,
    )
    checkpoints = (initial_checkpoint, final_checkpoint)
    step_rows = (
        step_row_from_step_result(
            step_result,
            identity=identity,
            family_extensions=lgrc9v3_step_family_extensions(model),
        ),
    )
    event_rows = event_rows_from_events(
        all_events,
        identity=identity,
        family_extensions_by_event=lgrc9v3_event_family_extensions_for_events(
            all_events
        ),
    )
    run_summary = run_summary_from_step_results(
        (step_result,),
        identity=identity,
        initial_observables=initial_observables,
        final_observables=model.compute_observables(),
        resolved_params=model.get_params().resolved_config,
        raw_params=model.get_params().raw_config,
        parameter_overrides={"example": "lgrc9v3_multi_basin_formation_bundle"},
        family_extensions=lgrc9v3_run_summary_family_extensions(model),
    )
    graph_index = checkpoint_index(identity, checkpoints)
    save_telemetry_artifact_pack(
        layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=run_summary,
        graph_checkpoint_index=graph_index,
        graph_checkpoints=checkpoints,
    )
    pack = TelemetryArtifactPack(
        layout=layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=run_summary,
        graph_checkpoint_index=graph_index,
        graph_checkpoints=checkpoints,
    )
    visual_layout = build_graph_run_visualization_layout(layout)
    render_graph_run_visual_bundle(pack, layout=visual_layout)

    final_multi_basin = run_summary.family_extensions["lgrc9v3"][
        "final_multi_basin_formation"
    ]
    topology_history = [
        {
            "kind": event.kind,
            "topology_mutated": bool(event.payload.get("topology_mutated", False)),
            "artifact_kind": event.payload.get("artifact_kind"),
            "selected_sink_id": event.payload.get("selected_sink_id"),
            "competing_sink_ids": event.payload.get("competing_sink_ids"),
            "losing_sink_ids": event.payload.get("losing_sink_ids"),
            "transferred_node_ids": event.payload.get("transferred_node_ids"),
        }
        for event in model.get_state().topology_event_log
    ]
    latest_child = model.get_state().child_basin_state_log[-1]
    return {
        "run_dir": display_path(layout.run_dir),
        "telemetry_dir": display_path(layout.telemetry_dir),
        "graph_checkpoint_index_path": display_path(
            layout.graph_checkpoint_index_path
        ),
        "graph_sequence_figure": display_path(visual_layout.sequence_figure_path),
        "graph_html": display_path(visual_layout.final_html_path),
        "event_counts_by_kind": event_counts,
        "initial_node_count": initial_checkpoint.node_count,
        "final_node_count": final_checkpoint.node_count,
        "initial_edge_count": initial_checkpoint.edge_count,
        "final_edge_count": final_checkpoint.edge_count,
        "topology_history": topology_history,
        "child_basin_core_ids": latest_child.child_basin_core_ids,
        "child_basin_membership_by_core": latest_child.child_basin_membership_by_core,
        "multi_basin_summary": final_multi_basin,
    }


def main() -> None:
    """Run the example and print artifact paths plus claim boundary."""

    artifacts = run_multi_basin_formation_bundle()
    print("LGRC9V3 multi-basin formation telemetry and visual bundle")
    print_json("artifacts", artifacts)
    print(
        "\nInterpretation: the saved telemetry/checkpoint artifacts expose an "
        "MB5 control-backed multi-basin formation candidate. MB6, native "
        "support, semantic learning, agency, and Phase 8 completion remain false."
    )
    print(
        "Geometry note: this fixture is a collapse/reabsorption telemetry and "
        "control example over an existing three-node graph. It does not show "
        "visible node birth; the topology-history records report "
        "topology_mutated=false and the child-basin state has one core whose "
        "membership covers the compact fixture."
    )


if __name__ == "__main__":
    main()
