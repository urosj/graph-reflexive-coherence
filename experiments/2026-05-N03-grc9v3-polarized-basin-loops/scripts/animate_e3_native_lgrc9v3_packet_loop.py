#!/usr/bin/env python3
"""Render the E3 native LGRC9V3 packet loop through PyGRC graph visuals."""

from __future__ import annotations

from collections import Counter
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
REPO_ROOT = EXPERIMENT_ROOT.parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

import run_e3_native_lgrc9v3_packet_loop_reproduction as e3  # noqa: E402
from pygrc.models.lgrc_9_v3_contract import (  # noqa: E402
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
)
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


RUN_ID = "e3-native-lgrc9v3-packet-loop-animation"
OUTPUT_ROOT = EXPERIMENT_ROOT / "outputs" / "e3_native_lgrc9v3_packet_loop_animation"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e3_native_lgrc9v3_packet_loop_animation.md"
SUMMARY_PATH = EXPERIMENT_ROOT / "outputs" / "e3_native_lgrc9v3_packet_loop_animation.json"

COMMAND = (
    "PYTHONPATH=src .venv/bin/python "
    "experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/"
    "animate_e3_native_lgrc9v3_packet_loop.py"
)


def _checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[Any, ...],
) -> GraphCheckpointIndex:
    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="e3_native_packet_loop_event_sequence",
        selection_params={
            "direction": "clockwise",
            "cycles": e3.N_CYCLES_MIN,
            "include_initial": True,
            "include_every_packet_step": True,
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


def _event_counts(events: tuple[Any, ...]) -> dict[str, int]:
    return dict(Counter(event.kind for event in events))


def _add_checkpoint(
    *,
    checkpoints: list[Any],
    model: Any,
    identity: RunTelemetryIdentity,
    label: str,
    reason: str,
    events: tuple[Any, ...] = (),
) -> None:
    checkpoints.append(
        build_lgrc9v3_graph_checkpoint(
            model,
            identity=identity,
            checkpoint_id=f"checkpoint-{len(checkpoints):08d}",
            checkpoint_label=label,
            checkpoint_reason=reason,
            event_count_window=len(events),
            event_counts_by_kind_window=_event_counts(events),
        )
    )


def _run_clockwise_with_checkpoints(
    identity: RunTelemetryIdentity,
) -> tuple[Any, tuple[Any, ...], tuple[Any, ...], tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    model = e3.LGRC9V3.from_state(e3.build_state(direction="clockwise"), {"dt": 1.0})
    route_aspect = e3.build_route_aspect(direction="clockwise")

    checkpoints: list[Any] = []
    step_results: list[Any] = []
    step_extensions: list[dict[str, Any]] = []
    producer_records: list[dict[str, Any]] = []
    _add_checkpoint(
        checkpoints=checkpoints,
        model=model,
        identity=identity,
        label="initial",
        reason="initial_clockwise_fixture",
    )

    last_channel = route_aspect.channels[-1]
    seed_hop = last_channel.route_hops[-1]
    model.schedule_packet_departure(
        source_node_id=seed_hop.source_node_id,
        target_node_id=seed_hop.target_node_id,
        edge_id=seed_hop.edge_id,
        amount=e3.SEED_RETURN_AMOUNT,
        departure_event_time_key=0.0,
        arrival_event_time_key=1.0,
        scheduler_event_index=1,
    )
    for seed_label in ("seed_departure", "seed_arrival"):
        result = model.step()
        step_results.append(result)
        step_extensions.append(lgrc9v3_step_family_extensions(model))
        _add_checkpoint(
            checkpoints=checkpoints,
            model=model,
            identity=identity,
            label=seed_label,
            reason=f"processed_{seed_label}",
            events=tuple(result.events),
        )

    for cycle_index in range(e3.N_CYCLES_MIN):
        for channel_id in route_aspect.channel_sequence:
            source_pole = channel_id.split("_to_")[0]
            e3._configure_trigger(
                model,
                route_aspect=route_aspect,
                source_pole_id=source_pole,
            )
            produced = model.produce_events(
                policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
            )
            producer_records.append(produced.to_artifact())
            _add_checkpoint(
                checkpoints=checkpoints,
                model=model,
                identity=identity,
                label=f"c{cycle_index + 1}_{source_pole}_producer",
                reason="post_surplus_trigger_producer",
            )
            if produced.scheduled_event_count != 1:
                raise RuntimeError(
                    f"expected one scheduled event for {source_pole}, "
                    f"got {produced.scheduled_event_count}"
                )
            departure = model.step()
            step_results.append(departure)
            step_extensions.append(lgrc9v3_step_family_extensions(model))
            _add_checkpoint(
                checkpoints=checkpoints,
                model=model,
                identity=identity,
                label=f"c{cycle_index + 1}_{source_pole}_departure",
                reason="packet_departure_processed",
                events=tuple(departure.events),
            )
            arrival = model.step()
            step_results.append(arrival)
            step_extensions.append(lgrc9v3_step_family_extensions(model))
            _add_checkpoint(
                checkpoints=checkpoints,
                model=model,
                identity=identity,
                label=f"c{cycle_index + 1}_{source_pole}_arrival",
                reason="packet_arrival_processed",
                events=tuple(arrival.events),
            )
    return (
        model,
        tuple(step_results),
        tuple(checkpoints),
        tuple(producer_records),
        tuple(step_extensions),
    )


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    identity = RunTelemetryIdentity(
        run_id=RUN_ID,
        model_family="LGRC9V3",
        params_identity=None,
        seed_name="n03-e3-native-four-pole-clockwise",
        seed_source_reference="run_e3_native_lgrc9v3_packet_loop_reproduction.py",
        seed_path=(
            "experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/"
            "run_e3_native_lgrc9v3_packet_loop_reproduction.py"
        ),
        param_family="n03_e3_native_lgrc9v3_packet_loop_visualization",
        requested_steps=2 + 2 * e3.N_CYCLES_MIN * len(e3.CW_NODE_ORDER),
    )
    (
        model,
        step_results,
        checkpoints,
        producer_records,
        step_extensions,
    ) = _run_clockwise_with_checkpoints(identity)
    all_events = tuple(event for result in step_results for event in result.events)
    step_rows = tuple(
        step_row_from_step_result(
            result,
            identity=identity,
            family_extensions=extension,
        )
        for result, extension in zip(
            step_results,
            step_extensions,
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
    initial_observables = {}
    final_observables = dict(model.compute_observables())
    run_summary = run_summary_from_step_results(
        step_results,
        identity=identity,
        initial_observables=initial_observables,
        final_observables=final_observables,
        resolved_params=model.get_params().resolved_config,
        raw_params=model.get_params().raw_config,
        parameter_overrides={
            "experiment": "N03",
            "surface": "E3 native LGRC9V3 packet-loop animation",
            "direction": "clockwise",
        },
        family_extensions=lgrc9v3_run_summary_family_extensions(model),
    )
    graph_index = _checkpoint_index(identity, checkpoints)
    layout = build_telemetry_artifact_layout(RUN_ID, root_dir=OUTPUT_ROOT)
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

    validation = e3.validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=model.snapshot()["events"],
        production_results=producer_records,
    )
    summary = {
        "status": "passed",
        "classification": "e3_native_lgrc9v3_packet_loop_standard_animation",
        "command": COMMAND,
        "source_command": e3.COMMAND,
        "run_id": RUN_ID,
        "direction": "clockwise",
        "native_lgrc9v3_execution": True,
        "native_packet_execution": True,
        "native_self_rearm_evidence": bool(validation["valid"]),
        "native_d2_3_equivalent": bool(validation["valid"])
        and int(validation["completed_count"]) // len(e3.CW_NODE_ORDER) >= e3.N_CYCLES_MIN,
        "completed_self_rearm_count": int(validation["completed_count"]),
        "cycle_count": int(validation["completed_count"]) // len(e3.CW_NODE_ORDER),
        "event_count": len(all_events),
        "checkpoint_count": len(checkpoints),
        "telemetry_dir": str(layout.telemetry_dir),
        "visualization_dir": str(visual_layout.run_dir),
        "graph_sequence_figure": str(visual_layout.sequence_figure_path),
        "graph_html": str(visual_layout.final_html_path),
        "graph_animation": str(visual_layout.animation_path),
        "movement_claim_allowed": False,
        "native_grc9v3_proposal_flux_loop_evidence": False,
    }
    _write_json(SUMMARY_PATH, summary)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "# E3 Native LGRC9V3 Packet-Loop Standard Animation\n\n"
        "Command:\n\n"
        "```bash\n"
        f"{COMMAND}\n"
        "```\n\n"
        "This animation is rendered through `pygrc.visualization` from saved "
        "LGRC9V3 telemetry graph checkpoints. It uses native E3 packet-loop "
        "execution and does not use the D2.3 prototype runner as the execution "
        "engine.\n\n"
        "Generated artifacts:\n\n"
        f"- Telemetry: `{layout.telemetry_dir}`\n"
        f"- Graph animation: `{visual_layout.animation_path}`\n"
        f"- Graph sequence: `{visual_layout.sequence_figure_path}`\n"
        f"- Final graph HTML: `{visual_layout.final_html_path}`\n"
        f"- Summary JSON: `{SUMMARY_PATH}`\n\n"
        "Summary:\n\n"
        "```json\n"
        f"{json.dumps(summary, indent=2, sort_keys=True)}\n"
        "```\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
