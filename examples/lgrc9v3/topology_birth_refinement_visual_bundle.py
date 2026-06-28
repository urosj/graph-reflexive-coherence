"""Capture a visible LGRC9V3 topology birth/refinement visual bundle.

What this example does:
    Runs the existing saturated-sink boundary-birth path used by the LGRC9V3
    runtime tests. The run schedules one packet departure and one causal
    boundary-birth trial, then processes the queue through packet departure,
    boundary birth / causal spark candidate emission, packet arrival,
    mechanical expansion, refinement packet transport, and proper-time
    inheritance. It saves graph checkpoints before the run and after each
    processed event so the visible topology change can be inspected.

What this example is not:
    It is not an MB5/MB6 multi-basin closeout, not native support evidence, not
    semantic learning, and not agency. It is a topology-growth visualization
    companion for `multi_basin_formation_bundle.py`, which is a separate
    collapse/reabsorption telemetry and control example over an unchanged
    three-node graph.
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
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX,
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
RUN_ID = "lgrc9v3-topology-birth-refinement-visual-bundle"


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


def saturated_sink_state() -> GRC9V3State:
    """Return the saturated-sink fixture used by LGRC9V3 boundary-birth tests."""

    graph = PortGraphBackend()
    center = graph.add_node({"label": "saturated_sink"})
    nodes = {
        center: GRC9V3NodeState(
            coherence=1.0,
            gradient_row_basis=[0.0, 0.0, 0.0],
            signed_hessian_row_basis=[1.0, 1.0, 1.0],
            basin_mass=1.0,
            basin_id="sink",
            depth=0,
        )
    }
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    for slot in range(9):
        port_id = slot + 1
        neighbor = graph.add_node({"label": f"neighbor_{port_id}"})
        edge_id = graph.connect_ports(
            center,
            slot,
            neighbor,
            0,
            {"kind": "saturated_sink_fixture"},
        )
        nodes[neighbor] = GRC9V3NodeState(
            coherence=1.0,
            basin_mass=1.0,
            basin_id=f"neighbor_{port_id}",
        )
        port_edges[edge_id] = PortEdge(
            center,
            port_id,
            neighbor,
            1,
            conductance=1.0,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = 1.0
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = 1.0
        flux_coupling[edge_id] = 0.0
    return GRC9V3State(
        topology=graph,
        nodes=nodes,
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
        sink_set={center},
        basins={center: set(nodes)},
    )


def topology_birth_refinement_params() -> dict[str, object]:
    """Return the opt-in topology-growth policies used by this visual example."""

    return {
        "dt": 1.0,
        "evolution": {
            "eps_gradient": 0.01,
            "eps_spark": 0.0,
            "eps_column_h": 1.0,
            "eps_column_h_crossing_zero": 0.0,
            "lambda_birth": 1.0,
            "alpha_seed": 0.1,
            "w_bond": 1.0,
        },
        "constitutive_semantic_modes": {
            "spark_lane": "grc9v3_column_h_assisted",
            "enable_column_h_sign_crossing": False,
            "store_previous_column_h": False,
        },
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
            "causal_collapse_reabsorption_allowed": False,
            "causal_identity_acceptance_allowed": False,
            "causal_boundary_birth_allowed": True,
            "causal_boundary_birth_policy": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX
            ),
        },
    }


def checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[object, ...],
) -> GraphCheckpointIndex:
    """Build a file-backed checkpoint index for saved telemetry artifacts."""

    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="initial+after-each-queue-event",
        selection_params={
            "include_initial": True,
            "include_after_each_queue_event": True,
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


def queue_has_work(model: LGRC9V3) -> bool:
    """Return whether the runtime has pending packet or boundary-birth work."""

    state = model.get_state()
    return bool(
        state.packet_ledger.event_queue_records
        or state.boundary_birth_trial_queue
    )


def run_topology_birth_refinement_visual_bundle(
    *,
    output_root: Path = EXAMPLE_OUTPUT_ROOT,
) -> dict[str, object]:
    """Run, save, and visualize the topology birth/refinement checkpoint bundle."""

    model = LGRC9V3.from_state(
        saturated_sink_state(),
        topology_birth_refinement_params(),
    )
    identity = RunTelemetryIdentity(
        run_id=RUN_ID,
        model_family="LGRC9V3",
        params_identity=model.get_params().params_hash,
        seed_name="saturated-sink-boundary-birth-fixture",
        seed_source_reference="examples/lgrc9v3/topology_birth_refinement_visual_bundle.py",
        seed_path="examples/lgrc9v3/topology_birth_refinement_visual_bundle.py",
        param_family="lgrc9v3_topology_birth_refinement_visual",
        requested_steps=3,
    )
    layout = build_telemetry_artifact_layout(RUN_ID, root_dir=output_root)
    initial_observables = dict(model.compute_observables())
    checkpoints = [
        build_lgrc9v3_graph_checkpoint(
            model,
            identity=identity,
            checkpoint_id="checkpoint-00000000",
            checkpoint_label="initial_saturated_sink",
            checkpoint_reason="initial",
        )
    ]

    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=0,
        edge_id=0,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.schedule_causal_boundary_birth_trial(
        parent_node_id=1,
        parent_port_id=2,
        outward_flux_pressure=2.0,
        event_time_key=1.5,
        scheduler_event_index=2,
        rng_sample=0.0,
        edge_delay=1.0,
    )

    step_results = []
    step_extensions = []
    while queue_has_work(model):
        result = model.step()
        step_results.append(result)
        step_extensions.append(lgrc9v3_step_family_extensions(model))
        step_event_counts = dict(Counter(event.kind for event in result.events))
        checkpoint_number = len(checkpoints)
        checkpoints.append(
            build_lgrc9v3_graph_checkpoint(
                model,
                identity=identity,
                checkpoint_id=f"checkpoint-{checkpoint_number:08d}",
                checkpoint_label=(
                    f"after_{result.bookkeeping['processed_event_kind']}"
                ),
                checkpoint_reason="after_queue_event",
                event_count_window=len(result.events),
                event_counts_by_kind_window=step_event_counts,
            )
        )

    step_results_tuple = tuple(step_results)
    all_events = tuple(
        event for result in step_results_tuple for event in result.events
    )
    event_counts = dict(Counter(event.kind for event in all_events))
    topology_event_kinds = tuple(
        event.kind for event in model.get_state().topology_event_log
    )
    checkpoint_node_counts = [
        checkpoint.node_count for checkpoint in checkpoints
    ]
    checkpoint_edge_counts = [
        checkpoint.edge_count for checkpoint in checkpoints
    ]

    step_rows = tuple(
        step_row_from_step_result(
            result,
            identity=identity,
            family_extensions=extension,
        )
        for result, extension in zip(
            step_results_tuple,
            tuple(step_extensions),
            strict=True,
        )
    )
    event_rows = event_rows_from_events(
        all_events,
        identity=identity,
        family_extensions_by_event=lgrc9v3_event_family_extensions_for_events(
            all_events
        ),
    )
    run_summary = run_summary_from_step_results(
        step_results_tuple,
        identity=identity,
        initial_observables=initial_observables,
        final_observables=model.compute_observables(),
        resolved_params=model.get_params().resolved_config,
        raw_params=model.get_params().raw_config,
        parameter_overrides={
            "example": "lgrc9v3_topology_birth_refinement_visual_bundle"
        },
        family_extensions=lgrc9v3_run_summary_family_extensions(model),
    )
    graph_index = checkpoint_index(identity, tuple(checkpoints))
    save_telemetry_artifact_pack(
        layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=run_summary,
        graph_checkpoint_index=graph_index,
        graph_checkpoints=tuple(checkpoints),
    )
    pack = TelemetryArtifactPack(
        layout=layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=run_summary,
        graph_checkpoint_index=graph_index,
        graph_checkpoints=tuple(checkpoints),
    )
    visual_layout = build_graph_run_visualization_layout(layout)
    render_graph_run_visual_bundle(pack, layout=visual_layout)

    return {
        "run_dir": display_path(layout.run_dir),
        "telemetry_dir": display_path(layout.telemetry_dir),
        "graph_checkpoint_index_path": display_path(
            layout.graph_checkpoint_index_path
        ),
        "graph_sequence_figure": display_path(visual_layout.sequence_figure_path),
        "graph_html": display_path(visual_layout.final_html_path),
        "event_counts_by_kind": event_counts,
        "topology_event_kinds": topology_event_kinds,
        "checkpoint_node_counts": checkpoint_node_counts,
        "checkpoint_edge_counts": checkpoint_edge_counts,
        "initial_node_count": checkpoint_node_counts[0],
        "final_node_count": checkpoint_node_counts[-1],
        "initial_edge_count": checkpoint_edge_counts[0],
        "final_edge_count": checkpoint_edge_counts[-1],
        "visible_topology_growth": (
            checkpoint_node_counts[-1] > checkpoint_node_counts[0]
            or checkpoint_edge_counts[-1] > checkpoint_edge_counts[0]
        ),
        "claim_boundary": {
            "mb5_or_mb6_claim": False,
            "native_support": False,
            "semantic_learning": False,
            "agency": False,
            "phase8_completion": False,
        },
    }


def main() -> None:
    """Run the example and print artifact paths plus claim boundary."""

    artifacts = run_topology_birth_refinement_visual_bundle()
    print("LGRC9V3 topology birth/refinement visual bundle")
    print_json("artifacts", artifacts)
    print(
        "\nInterpretation: this bundle demonstrates visible LGRC9V3 topology "
        "growth through the existing boundary-birth/refinement path. It is a "
        "visual and telemetry example, not an MB5/MB6 closeout, not native "
        "support, not semantic learning, not agency, and not Phase 8 completion."
    )


if __name__ == "__main__":
    main()
