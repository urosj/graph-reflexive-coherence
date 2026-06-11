"""Spark a small landscape-backed GRC9V3 cell and render the result.

This is the first-contact example.

What it does:
    1. Loads a rich landscape seed from `configs/landscapes/seed/`.
    2. Extracts and compiles the GRCL9V3 landscape extension.
    3. Lowers the source into a `GRC9V3` runtime state.
    4. Runs one full model step.
    5. Captures telemetry.
    6. Renders behavior and graph visuals.

Why this is the quickstart:
    It gives a user something visible and dynamic immediately: a seed-backed
    runtime produces spark/expansion/choice events, and the output directory
    contains plots plus an interactive final graph.

Where to go next:
    - `examples/grc9v3/` explains lanes, event evidence, telemetry, visuals.
    - `examples/landscapes/` explains seed definition, validation, lowering.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if SRC_ROOT.exists() and str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.core import StepResult  # noqa: E402
from pygrc.landscapes import load_landscape_seed, validate_landscape_seed  # noqa: E402
from pygrc.landscapes.extensions.grcl9v3 import (  # noqa: E402
    compile_grcl9v3_landscape_example_to_source,
    extract_grcl9v3_landscape_example_from_seed,
)
from pygrc.models import GRC9V3, lower_grcl9v3_source_to_grc9v3_state  # noqa: E402
from pygrc.telemetry import (  # noqa: E402
    GraphCheckpointArtifact,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    TelemetryCaptureConfig,
    build_run_id,
    build_telemetry_artifact_layout,
    capture_run_telemetry,
    load_telemetry_artifact_pack,
)
from pygrc.visualization import (  # noqa: E402
    DEFAULT_GRC9V3_RUN_OBSERVABLES,
    build_graph_run_visualization_layout,
    build_run_visualization_layout,
    render_graph_run_visual_bundle,
    render_run_visual_bundle,
)


SEED_PATH = Path(
    "configs/landscapes/seed/grcl9v3-corrected-hybrid-full-composition.seed.yaml"
)
OUTPUT_ROOT = Path("outputs/examples/quickstart")
RUN_NAME = "spark_a_cell"


def _load_model() -> tuple[GRC9V3, dict[str, Any]]:
    """Load a landscape seed and lower it into a GRC9V3 model."""

    seed = load_landscape_seed(SEED_PATH)
    validate_landscape_seed(seed)
    example = extract_grcl9v3_landscape_example_from_seed(seed, seed_path=SEED_PATH)
    if example is None:
        raise RuntimeError(f"{SEED_PATH} does not declare a GRCL9V3 landscape example")

    source = compile_grcl9v3_landscape_example_to_source(example)
    config = {"dt": seed.constitutive_profile.dt}
    lowering = lower_grcl9v3_source_to_grc9v3_state(source, params=config)
    model = GRC9V3.from_state(lowering.state, config)
    return model, {
        "seed_name": seed.meta.name,
        "seed_path": str(SEED_PATH),
        "example_name": example.example_name,
        "source_construct_kinds": [
            construct.construct_kind for construct in source.constructs
        ],
    }


def _identity(model: GRC9V3, metadata: dict[str, Any]) -> RunTelemetryIdentity:
    """Create a telemetry identity shared by rows and graph checkpoints."""

    params = model.get_params()
    run_id = build_run_id(
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=str(metadata["seed_name"]),
        seed_source_reference=str(SEED_PATH),
        seed_path=str(SEED_PATH),
        param_family="quickstart",
        rng_seed=None,
        requested_steps=1,
        overrides={"quickstart": RUN_NAME},
    )
    return RunTelemetryIdentity(
        run_id=run_id,
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=str(metadata["seed_name"]),
        seed_source_reference=str(SEED_PATH),
        seed_path=str(SEED_PATH),
        param_family="quickstart",
        rng_seed=None,
        requested_steps=1,
    )


def _event_counts(events: list[Any]) -> dict[str, int]:
    return dict(Counter(event.kind for event in events))


def _checkpoint(
    model: GRC9V3,
    *,
    identity: RunTelemetryIdentity,
    checkpoint_id: str,
    label: str,
    reason: str,
    event_counts_by_kind: dict[str, int] | None = None,
) -> GraphCheckpointArtifact:
    """Export the small graph surface needed for quickstart visuals."""

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
                "payload": {"role": "sink" if int(node_id) in state.sink_set else "node"},
            }
        )

    edge_records: list[dict[str, Any]] = []
    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = state.topology.edge_ports(int(edge_id))
        edge_records.append(
            {
                "edge_id": int(edge_id),
                "source_node_id": int(endpoint_a[0]),
                "source_port_id": int(endpoint_a[1]) + 1,
                "target_node_id": int(endpoint_b[0]),
                "target_port_id": int(endpoint_b[1]) + 1,
                "base_conductance": state.base_conductance.get(int(edge_id), 0.0),
            }
        )

    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=state.step_index,
        time=state.time,
        checkpoint_label=label,
        checkpoint_reason=reason,
        graph_kind="port_graph",
        node_count=len(node_records),
        edge_count=len(edge_records),
        node_records=tuple(node_records),
        edge_records=tuple(edge_records),
        event_step_range={
            "start_step_inclusive": state.step_index,
            "end_step_inclusive": state.step_index,
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


def run_quickstart() -> dict[str, Any]:
    """Run the quickstart and return paths to visible artifacts."""

    model, metadata = _load_model()
    params = model.get_params()
    identity = _identity(model, metadata)
    layout = build_telemetry_artifact_layout(RUN_NAME, root_dir=OUTPUT_ROOT)

    initial_observables = dict(model.compute_observables())
    initial_checkpoint = _checkpoint(
        model,
        identity=identity,
        checkpoint_id="step-00000000",
        label="initial",
        reason="initial",
    )

    step_result = model.step()
    event_counts = _event_counts(step_result.events)
    final_checkpoint = _checkpoint(
        model,
        identity=identity,
        checkpoint_id="step-00000001",
        label="final",
        reason="final",
        event_counts_by_kind=event_counts,
    )
    checkpoints = (initial_checkpoint, final_checkpoint)

    telemetry = capture_run_telemetry(
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=str(metadata["seed_name"]),
        seed_source_reference=str(SEED_PATH),
        seed_path=str(SEED_PATH),
        param_family="quickstart",
        rng_seed=None,
        requested_steps=1,
        initial_observables=initial_observables,
        step_results=(
            StepResult(
                step_index=step_result.step_index,
                time=step_result.time,
                events=step_result.events,
                observables=step_result.observables,
                bookkeeping={"quickstart": RUN_NAME},
            ),
        ),
        final_observables=step_result.observables,
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        overrides={"quickstart": RUN_NAME},
        graph_checkpoints=checkpoints,
        graph_checkpoint_index=_checkpoint_index(identity, checkpoints),
        artifact_layout=layout,
        config=TelemetryCaptureConfig(root_dir=OUTPUT_ROOT, write_artifacts=True),
    )

    pack = load_telemetry_artifact_pack(layout)
    behavior_layout = build_run_visualization_layout(layout)
    graph_layout = build_graph_run_visualization_layout(layout)
    render_run_visual_bundle(
        pack,
        layout=behavior_layout,
        observables=DEFAULT_GRC9V3_RUN_OBSERVABLES,
    )
    render_graph_run_visual_bundle(pack, layout=graph_layout)

    return {
        "title": "Spark a Cell",
        "seed_name": metadata["seed_name"],
        "seed_path": metadata["seed_path"],
        "source_construct_kinds": metadata["source_construct_kinds"],
        "event_counts": event_counts,
        "run_id": telemetry.identity.run_id,
        "open_these": {
            "event_timeline": str(behavior_layout.event_timeline_path),
            "trajectories": str(behavior_layout.trajectory_figure_path),
            "graph_sequence": str(graph_layout.sequence_figure_path),
            "final_graph_html": str(graph_layout.final_html_path),
            "graph_animation": str(graph_layout.animation_path),
        },
        "telemetry": {
            "steps": str(layout.step_rows_path),
            "events": str(layout.event_rows_path),
            "summary": str(layout.run_summary_path),
        },
    }


def main() -> None:
    print("PyGRC Quickstart: Spark a Cell")
    print(json.dumps(run_quickstart(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
