"""Capture a small GRC9V3 Lane B run into telemetry artifacts.

What this example does:
    Loads the same explicit runtime fixture as the first examples, runs the
    spark layer under Lane B, captures telemetry rows, writes a run summary,
    and saves graph checkpoints under `outputs/examples/grc9v3/`.

Why it is needed:
    Event payloads are useful in memory, but reports and visuals consume
    telemetry artifacts. This script shows the runner boundary:
    runtime events -> `StepResult` -> `capture_run_telemetry(...)`.

Important boundary:
    This is a one-step spark-layer example, not a full landscape experiment.
    It deliberately captures the Lane B candidate/expansion surface exposed by
    `apply_hybrid_sparks()`.

Alternatives:
    Use `model.step()` for complete runtime dynamics. Use landscape examples
    when the source is an authored landscape seed. Use experiment runners under
    `experiments/` for full evidence suites.

References:
    docs/reference/Telemetry-ReferenceGuide.md
    docs/reference/GRC-Runtime-ReferenceGuide.md
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from _fixtures import (
    GRC9V3,
    LANE_B,
    event_counts,
    make_column_h_state,
    make_config,
    print_json,
)
from pygrc.core import StepResult
from pygrc.telemetry import (
    GraphCheckpointArtifact,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    TelemetryCaptureConfig,
    build_run_id,
    build_telemetry_artifact_layout,
    capture_run_telemetry,
)


EXAMPLE_OUTPUT_ROOT = Path("outputs/examples/grc9v3")
TELEMETRY_RUN_DIR_NAME = "lane_b_column_h_telemetry"
SEED_NAME = "examples_grc9v3_column_h_fixture"


def _run_identity(model: GRC9V3, *, requested_steps: int) -> RunTelemetryIdentity:
    """Build the telemetry identity used by rows and graph checkpoints.

    Why it is needed:
        Graph checkpoints are created before calling `capture_run_telemetry`,
        so they need the same identity that the telemetry recorder will use.

    Alternative:
        Larger runners usually let their orchestration layer own identity and
        pass it consistently to telemetry/checkpoint builders.
    """

    params = model.get_params()
    run_id = build_run_id(
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=SEED_NAME,
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="example_lane_b_column_h",
        rng_seed=None,
        requested_steps=requested_steps,
        overrides={"runner": "apply_hybrid_sparks"},
    )
    return RunTelemetryIdentity(
        run_id=run_id,
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=SEED_NAME,
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="example_lane_b_column_h",
        rng_seed=None,
        requested_steps=requested_steps,
    )


def _checkpoint(
    model: GRC9V3,
    *,
    identity: RunTelemetryIdentity,
    checkpoint_id: str,
    step_index: int,
    time: float,
    label: str,
    reason: str,
    event_counts_by_kind: dict[str, int] | None = None,
) -> GraphCheckpointArtifact:
    """Build the graph checkpoint needed by graph visualization.

    Why it is needed:
        `render_graph_run_visual_bundle(...)` renders saved graph checkpoints,
        not live models. The checkpoint records here are intentionally small:
        node id/coherence/sink status and edge id/endpoints/conductance.

    Alternative:
        Full experiment runners usually export richer checkpoint overlays.
    """

    state = model.get_state()
    node_records: list[dict[str, Any]] = []
    for node_id in sorted(state.topology.iter_live_node_ids()):
        node_state = state.nodes[int(node_id)]
        node_records.append(
            {
                "node_id": int(node_id),
                "coherence": node_state.coherence,
                "sink_flag": int(node_id) in state.sink_set,
                "active_degree": len(tuple(state.topology.incident_edge_ids(int(node_id)))),
                "column_h_branch_hit": (
                    int(node_id) == 0
                    and any(
                        event.kind == "hybrid_spark_candidate"
                        and bool(event.payload.get("column_h_branch_hit"))
                        for event in state.event_log
                    )
                ),
                "payload": {"role": "center_sink" if int(node_id) == 0 else "neighbor"},
            }
        )

    edge_records: list[dict[str, Any]] = []
    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = state.topology.edge_ports(int(edge_id))
        edge_records.append(
            {
                "edge_id": int(edge_id),
                "source_node_id": int(endpoint_a[0]),
                "target_node_id": int(endpoint_b[0]),
                "source_port_id": int(endpoint_a[1]) + 1,
                "target_port_id": int(endpoint_b[1]) + 1,
                "base_conductance": state.base_conductance.get(int(edge_id), 0.0),
            }
        )

    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=time,
        checkpoint_label=label,
        checkpoint_reason=reason,
        graph_kind="port_graph",
        node_count=len(node_records),
        edge_count=len(edge_records),
        node_records=tuple(node_records),
        edge_records=tuple(edge_records),
        event_step_range={
            "start_step_inclusive": step_index,
            "end_step_inclusive": step_index,
        },
        event_count_window=sum((event_counts_by_kind or {}).values()),
        event_counts_by_kind_window=event_counts_by_kind or {},
        flow_representation="base_conductance_only",
        flow_cadence="checkpoint_only",
    )


def _checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[GraphCheckpointArtifact, ...],
) -> GraphCheckpointIndex:
    """Build the file-backed checkpoint index saved by telemetry I/O."""

    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="initial+final",
        selection_params={"include_initial": True, "include_final": True},
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


def capture_example_telemetry() -> dict[str, Any]:
    """Run the example and write telemetry artifacts.

    Returns a small summary so `visual_bundle.py` can reuse this function when
    artifacts are missing.
    """

    model = GRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    params = model.get_params()
    requested_steps = 1
    identity = _run_identity(model, requested_steps=requested_steps)
    layout = build_telemetry_artifact_layout(
        TELEMETRY_RUN_DIR_NAME,
        root_dir=EXAMPLE_OUTPUT_ROOT,
    )

    initial_observables = dict(model.compute_observables())
    initial_checkpoint = _checkpoint(
        model,
        identity=identity,
        checkpoint_id="step-00000000",
        step_index=0,
        time=0.0,
        label="initial",
        reason="initial",
    )

    events = model.apply_hybrid_sparks()
    event_count_by_kind = event_counts(events)
    final_observables = dict(model.compute_observables())
    step_result = StepResult(
        step_index=1,
        time=params.dt,
        events=events,
        observables=final_observables,
        bookkeeping={"example_runner": "apply_hybrid_sparks"},
    )
    final_checkpoint = _checkpoint(
        model,
        identity=identity,
        checkpoint_id="step-00000001",
        step_index=1,
        time=params.dt,
        label="final",
        reason="final",
        event_counts_by_kind=event_count_by_kind,
    )
    checkpoints = (initial_checkpoint, final_checkpoint)

    telemetry = capture_run_telemetry(
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=SEED_NAME,
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="example_lane_b_column_h",
        rng_seed=None,
        requested_steps=requested_steps,
        initial_observables=initial_observables,
        step_results=(step_result,),
        final_observables=final_observables,
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        overrides={"runner": "apply_hybrid_sparks"},
        graph_checkpoints=checkpoints,
        graph_checkpoint_index=_checkpoint_index(identity, checkpoints),
        artifact_layout=layout,
        config=TelemetryCaptureConfig(
            root_dir=EXAMPLE_OUTPUT_ROOT,
            write_artifacts=True,
        ),
    )

    return {
        "run_id": telemetry.identity.run_id,
        "artifact_run_dir": str(layout.run_dir),
        "telemetry_dir": str(layout.telemetry_dir),
        "steps_path": str(layout.step_rows_path),
        "events_path": str(layout.event_rows_path),
        "run_summary_path": str(layout.run_summary_path),
        "graph_checkpoint_index_path": str(layout.graph_checkpoint_index_path),
        "step_rows": len(telemetry.step_rows),
        "event_rows": len(telemetry.event_rows),
        "event_counts_by_kind": dict(Counter(row.event_kind for row in telemetry.event_rows)),
        "graph_checkpoints": len(telemetry.graph_checkpoints),
    }


def main() -> None:
    """Capture telemetry and print artifact paths."""

    print("GRC9V3 Lane B telemetry capture")
    print_json("telemetry_capture", capture_example_telemetry())


if __name__ == "__main__":
    main()
