"""Capture LGRC9V3 telemetry and render graph visual artifacts.

What this example does:
    Runs a small executable `LGRC9V3` queue, saves telemetry rows and graph
    checkpoints under `outputs/examples/lgrc9v3/`, and renders the graph visual
    bundle from those checkpoint artifacts.

Why it is needed:
    LGRC9V3 telemetry and visualization are artifact-driven. The model run
    produces causal event-time/proper-time evidence; telemetry records it; graph
    rendering reads the checkpoint overlays. This script shows the whole path.

Alternatives:
    Use `examples/grc9v3/telemetry_capture.py` for synchronous GRC9V3 Lane B
    telemetry. Use this script when you need LGRC9V3 causal clocks, packet
    ledgers, and causal spark diagnostics in the artifact.
"""

from __future__ import annotations

from collections import Counter
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
GRC9V3_EXAMPLES = REPO_ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, make_column_h_state, make_config  # noqa: E402
from pygrc.models import LGRC9V3  # noqa: E402
from pygrc.telemetry import (  # noqa: E402
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
from pygrc.visualization import (  # noqa: E402
    build_graph_run_visualization_layout,
    render_graph_run_visual_bundle,
)


EXAMPLE_OUTPUT_ROOT = REPO_ROOT / "outputs" / "examples" / "lgrc9v3"
RUN_ID = "lgrc9v3-executable-telemetry-visual-bundle"


def print_json(label: str, payload: object) -> None:
    """Print deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(payload, indent=2, sort_keys=True))


def checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[object, ...],
) -> GraphCheckpointIndex:
    """Build the simple file-backed checkpoint index used by telemetry I/O."""

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


def main() -> None:
    """Run LGRC9V3, save telemetry, and render graph visual output."""

    model = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    identity = RunTelemetryIdentity(
        run_id=RUN_ID,
        model_family="LGRC9V3",
        params_identity=model.get_params().params_hash,
        seed_name="example-column-h-fixture",
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="lgrc9v3_executable_lane_b",
        requested_steps=2,
    )
    layout = build_telemetry_artifact_layout(RUN_ID, root_dir=EXAMPLE_OUTPUT_ROOT)
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
        target_node_id=0,
        edge_id=0,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    step_results_list = []
    step_extensions = []
    while model.get_state().packet_ledger.event_queue_records:
        result = model.step()
        step_results_list.append(result)
        step_extensions.append(lgrc9v3_step_family_extensions(model))
    step_results = tuple(step_results_list)
    all_events = tuple(event for result in step_results for event in result.events)
    event_counts = dict(Counter(event.kind for event in all_events))
    final_checkpoint = build_lgrc9v3_graph_checkpoint(
        model,
        identity=identity,
        checkpoint_id="checkpoint-00000001",
        checkpoint_label="after_queue",
        checkpoint_reason="final",
        event_count_window=len(all_events),
        event_counts_by_kind_window=event_counts,
    )
    checkpoints = (initial_checkpoint, final_checkpoint)

    step_rows = tuple(
        step_row_from_step_result(
            result,
            identity=identity,
            family_extensions=extension,
        )
        for result, extension in zip(step_results, step_extensions, strict=True)
    )
    event_rows = event_rows_from_events(
        all_events,
        identity=identity,
        family_extensions_by_event=lgrc9v3_event_family_extensions_for_events(
            all_events
        ),
    )
    summary = run_summary_from_step_results(
        step_results,
        identity=identity,
        initial_observables=initial_observables,
        final_observables=model.compute_observables(),
        resolved_params=model.get_params().resolved_config,
        raw_params=model.get_params().raw_config,
        parameter_overrides={"example": "lgrc9v3_telemetry_visual_bundle"},
        family_extensions=lgrc9v3_run_summary_family_extensions(model),
    )
    graph_index = checkpoint_index(identity, checkpoints)
    save_telemetry_artifact_pack(
        layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=summary,
        graph_checkpoint_index=graph_index,
        graph_checkpoints=checkpoints,
    )
    pack = TelemetryArtifactPack(
        layout=layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=summary,
        graph_checkpoint_index=graph_index,
        graph_checkpoints=checkpoints,
    )
    visual_layout = build_graph_run_visualization_layout(layout)
    render_graph_run_visual_bundle(pack, layout=visual_layout)

    print("LGRC9V3 telemetry and visual bundle")
    print_json(
        "artifacts",
        {
            "run_dir": str(layout.run_dir),
            "telemetry_dir": str(layout.telemetry_dir),
            "event_rows_path": str(layout.event_rows_path),
            "graph_checkpoint_index_path": str(layout.graph_checkpoint_index_path),
            "graph_sequence_figure": str(visual_layout.sequence_figure_path),
            "graph_html": str(visual_layout.final_html_path),
            "event_counts_by_kind": event_counts,
        },
    )
    print(
        "\nInterpretation: telemetry records LGRC9V3 causal event rows and graph "
        "checkpoint overlays. Visualization renders those artifacts; it does "
        "not add new runtime evidence."
    )


if __name__ == "__main__":
    main()
