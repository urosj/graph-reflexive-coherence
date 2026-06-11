"""Run a dense single-seed GRCV3 rich fulltest lane.

This script is the family-native counterpart to the shared
`run_representative_fulltest.py` lane. It is intentionally single-seed and
does not try to preserve cross-family comparability; its role is to exercise a
rich `GRCL-v3` seed under the same dense artifact envelope:

- one rich seed
- `150` steps by default
- graph checkpoints captured every step
- graph checkpoint chunk size `25`
- flow overlays enabled
- behavior and graph visualization rendered by default

Artifacts are written under:

- `outputs/<experiment_id>/grcv3-rich/<profile>/<seed-stem>/<run_id>/...`

The default runtime envelope also enables the first explicit choice/collapse
backend:

- `choice = sink_compatibility`
- `epsilon_choice = 0.15`
- `epsilon_collapse = 0.14`
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.core import build_backend_selection, build_backend_selection_payload
from pygrc.models import build_grcv3_from_landscape_seed, run_grcv3_landscape_seed
from pygrc.models.grc_v3_checkpoints import export_grcv3_graph_checkpoint
from pygrc.telemetry import (
    DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    GraphCheckpointCaptureConfig,
    GraphCheckpointChunkWriter,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    TelemetryCaptureConfig,
    build_run_experiment_report,
    build_run_id,
    build_telemetry_artifact_layout,
    capture_run_telemetry,
    classify_grcv3_event_extension,
    grcv3_event_family_extensions,
    grcv3_run_summary_family_extensions,
    grcv3_step_family_extensions,
    load_telemetry_artifact_pack,
    save_experiment_report,
)
from pygrc.telemetry.experiments import (
    _build_grcv3_landscape_run_summary,
    _build_grcv3_landscape_step_observability,
    _build_grcv3_run_summary_extension,
    _build_grcv3_step_extension,
    _to_plain_data,
)
from pygrc.visualization import (
    DEFAULT_GRCV3_RUN_OBSERVABLES,
    SUPPORTED_SURFACE_MODES,
    SURFACE_MODE_ALL,
    SURFACE_MODE_BEHAVIOR,
    SURFACE_MODE_GRAPH,
    build_graph_run_visualization_layout,
    build_run_visualization_layout,
    render_graph_run_visual_bundle,
    render_run_visual_bundle,
)


DEFAULT_OUTPUTS_ROOT = Path("outputs")
DEFAULT_EXPERIMENT_ID = "grcv3-rich-fulltest"
DEFAULT_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-basin-boundary-channel-probe.seed.yaml"
)
DEFAULT_PROFILE_NAME = DEFAULT_GRCV3_LANDSCAPE_PROFILE
DEFAULT_STEPS = 150
DEFAULT_GRAPH_CHUNK_SIZE = 25
DEFAULT_SURFACE_MODE = "all"
DEFAULT_CHOICE_BACKEND = "sink_compatibility"
DEFAULT_EPSILON_CHOICE = 0.15
DEFAULT_EPSILON_COLLAPSE = 0.14


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the dense single-seed GRCV3 rich fulltest and, by default, "
            "render the matching behavior and graph visualization outputs."
        )
    )
    parser.add_argument(
        "--outputs-root",
        default=str(DEFAULT_OUTPUTS_ROOT),
        help="Project-relative artifact root.",
    )
    parser.add_argument(
        "--experiment-id",
        default=DEFAULT_EXPERIMENT_ID,
        help="Experiment id written directly under the outputs root.",
    )
    parser.add_argument(
        "--seed",
        default=str(DEFAULT_SEED),
        help="Relative path to the rich GRCV3 seed file.",
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE_NAME,
        help="GRCV3 rich landscape profile name.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of GRCV3 steps to run.",
    )
    parser.add_argument(
        "--graph-chunk-size",
        type=int,
        default=DEFAULT_GRAPH_CHUNK_SIZE,
        help="Chunk size for dense graph-checkpoint JSONL storage.",
    )
    parser.add_argument(
        "--surface",
        choices=SUPPORTED_SURFACE_MODES,
        default=DEFAULT_SURFACE_MODE,
        help=(
            "Visualization surface to render after telemetry is written. "
            "Use --skip-visuals to suppress rendering entirely."
        ),
    )
    parser.add_argument(
        "--skip-visuals",
        action="store_true",
        help="Write telemetry only and do not render visualization artifacts.",
    )
    return parser


def _seed_lane_name(seed_path: Path) -> str:
    name = seed_path.name
    for suffix in (".seed.yaml", ".yaml", ".yml", ".json"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return seed_path.stem


def _default_choice_collapse_overrides() -> dict[str, Any]:
    return {
        "constitutive_semantic_modes": {
            "backend_selections": build_backend_selection_payload(
                [
                    build_backend_selection(
                        category="choice",
                        name=DEFAULT_CHOICE_BACKEND,
                        params={
                            "epsilon_choice": DEFAULT_EPSILON_CHOICE,
                            "epsilon_collapse": DEFAULT_EPSILON_COLLAPSE,
                        },
                    )
                ]
            )
        }
    }


def _capture_single_grcv3_landscape_run(
    *,
    run: Any,
    telemetry_root: Path,
    telemetry_experiment_path: Path,
    num_steps: int,
    checkpoint_chunk_size: int,
    overrides: dict[str, Any],
) -> Any:
    params = run.model.get_params()
    checkpoint_config = GraphCheckpointCaptureConfig(
        include_initial=True,
        include_final=True,
        every_step=True,
        include_flow_overlays=True,
        storage_mode="jsonl_chunks",
        chunk_size=checkpoint_chunk_size,
    )
    run_identity = RunTelemetryIdentity(
        run_id=build_run_id(
            model_family="grcv3",
            params_identity=params.params_hash,
            seed_name=run.request.seed.meta.name,
            seed_source_reference=run.request.seed.meta.source_reference,
            seed_path=(
                None if run.request.seed_path is None else str(run.request.seed_path)
            ),
            param_family=run.request.profile_name,
            rng_seed=None,
            requested_steps=num_steps,
            overrides=overrides,
        ),
        model_family="grcv3",
        params_identity=params.params_hash,
        seed_name=run.request.seed.meta.name,
        seed_source_reference=run.request.seed.meta.source_reference,
        seed_path=(None if run.request.seed_path is None else str(run.request.seed_path)),
        param_family=run.request.profile_name,
        rng_seed=None,
        requested_steps=num_steps,
    )
    streamed_artifact_layout = build_telemetry_artifact_layout(
        run_identity.run_id,
        root_dir=telemetry_root,
        experiment_path=telemetry_experiment_path,
    )
    checkpoint_chunk_writer = GraphCheckpointChunkWriter(
        streamed_artifact_layout,
        chunk_size=checkpoint_config.chunk_size,
    )
    streamed_checkpoint_references: list[GraphCheckpointReference] = []
    step_family_extensions: list[dict[str, dict[str, Any]]] = []
    event_family_extensions_by_step: list[list[dict[str, dict[str, Any]]]] = []

    def record_graph_checkpoint(checkpoint: Any) -> None:
        streamed_checkpoint_references.append(checkpoint_chunk_writer.write(checkpoint))

    replay_model = build_grcv3_from_landscape_seed(
        run.request.seed,
        params=_to_plain_data(params.raw_config),
        profile_name=run.request.profile_name,
        validate_seed=False,
    )
    replay_model.rebuild_basin_attributes()
    replay_model.rebuild_identity_state()
    initial_transient_landscape = _build_grcv3_landscape_step_observability(replay_model)

    record_graph_checkpoint(
        export_grcv3_graph_checkpoint(
            replay_model,
            identity=run_identity,
            checkpoint_id="step-00000000",
            checkpoint_label="initial",
            checkpoint_reason="initial",
            event_step_range={"start_step_inclusive": 0, "end_step_inclusive": 0},
            event_count_window=0,
            event_counts_by_kind_window={},
            include_flow_overlays=True,
        )
    )

    last_checkpoint_step_index = 0
    event_counts_since_checkpoint: dict[str, int] = {}
    event_count_since_checkpoint = 0
    transient_landscape_steps = []
    for _ in range(num_steps):
        step_result = replay_model.step()
        transient_landscape = _build_grcv3_landscape_step_observability(replay_model)
        transient_landscape_steps.append(transient_landscape)
        step_family_extensions.append(
            dict(
                grcv3_step_family_extensions(
                    _build_grcv3_step_extension(
                        replay_model,
                        transient_landscape=transient_landscape,
                    )
                )
            )
        )
        event_family_extensions_by_step.append(
            [
                dict(
                    grcv3_event_family_extensions(
                        classify_grcv3_event_extension(event.kind, event.payload)
                    )
                )
                for event in step_result.events
            ]
        )
        for event in step_result.events:
            event_counts_since_checkpoint[event.kind] = (
                event_counts_since_checkpoint.get(event.kind, 0) + 1
            )
        event_count_since_checkpoint += len(step_result.events)

        checkpoint_label = "interval"
        checkpoint_reason = "interval"
        if step_result.step_index == num_steps:
            checkpoint_label = "final"
            checkpoint_reason = "final"
        record_graph_checkpoint(
            export_grcv3_graph_checkpoint(
                replay_model,
                identity=run_identity,
                checkpoint_id=f"step-{step_result.step_index:08d}",
                checkpoint_label=checkpoint_label,
                checkpoint_reason=checkpoint_reason,
                event_step_range={
                    "start_step_inclusive": last_checkpoint_step_index + 1,
                    "end_step_inclusive": step_result.step_index,
                },
                event_count_window=event_count_since_checkpoint,
                event_counts_by_kind_window=dict(
                    sorted(event_counts_since_checkpoint.items())
                ),
                include_flow_overlays=True,
            )
        )
        last_checkpoint_step_index = step_result.step_index
        event_counts_since_checkpoint = {}
        event_count_since_checkpoint = 0

    summary_family_extensions = grcv3_run_summary_family_extensions(
        _build_grcv3_run_summary_extension(
            run.model,
            run.step_results,
            transient_landscape=_build_grcv3_landscape_run_summary(
                run.model,
                initial_observability=initial_transient_landscape,
                step_observability=tuple(transient_landscape_steps),
                step_results=run.step_results,
            ),
        )
    )
    graph_checkpoint_index = GraphCheckpointIndex(
        identity=run_identity,
        selection_policy=checkpoint_config.selection_policy,
        selection_params=checkpoint_config.selection_params,
        checkpoints=tuple(streamed_checkpoint_references),
    )
    return capture_run_telemetry(
        model_family="grcv3",
        params_identity=params.params_hash,
        seed_name=run.request.seed.meta.name,
        seed_source_reference=run.request.seed.meta.source_reference,
        seed_path=(None if run.request.seed_path is None else str(run.request.seed_path)),
        param_family=run.request.profile_name,
        rng_seed=None,
        requested_steps=num_steps,
        initial_observables=run.initial_observables,
        step_results=run.step_results,
        final_observables=run.final_observables,
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        overrides=overrides,
        step_family_extensions=step_family_extensions,
        event_family_extensions_by_step=event_family_extensions_by_step,
        summary_family_extensions=summary_family_extensions,
        graph_checkpoints=(),
        graph_checkpoint_index=graph_checkpoint_index,
        artifact_layout=streamed_artifact_layout,
        config=TelemetryCaptureConfig(
            root_dir=telemetry_root,
            experiment_path=telemetry_experiment_path,
            write_artifacts=True,
            graph_checkpoints=checkpoint_config,
        ),
    )


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    outputs_root = Path(args.outputs_root)
    seed_path = Path(args.seed)
    seed_lane_name = _seed_lane_name(seed_path)
    experiment_path = Path(args.experiment_id) / "grcv3-rich" / args.profile / seed_lane_name
    overrides = _default_choice_collapse_overrides()

    run = run_grcv3_landscape_seed(
        seed_path,
        profile_name=args.profile,
        overrides=overrides,
        num_steps=args.steps,
    )
    telemetry = _capture_single_grcv3_landscape_run(
        run=run,
        telemetry_root=outputs_root,
        telemetry_experiment_path=experiment_path,
        num_steps=args.steps,
        checkpoint_chunk_size=args.graph_chunk_size,
        overrides=overrides,
    )
    if telemetry.artifact_layout is None:
        raise RuntimeError("rich GRCV3 fulltest did not write telemetry artifacts")

    experiment_report = build_run_experiment_report(
        telemetry.run_summary,
        step_rows=telemetry.step_rows,
        artifact_layout=telemetry.artifact_layout,
    )
    save_experiment_report(
        telemetry.artifact_layout.experiment_report_path,
        experiment_report,
    )
    pack = load_telemetry_artifact_pack(telemetry.artifact_layout)

    print("GRCV3 rich fulltest telemetry complete.")
    print(f"experiment_id={args.experiment_id}")
    print(f"seed={seed_path.as_posix()}")
    print(f"seed_lane={seed_lane_name}")
    print(f"profile={args.profile}")
    print(f"steps={args.steps}")
    print(f"default_choice_backend={DEFAULT_CHOICE_BACKEND}")
    print(f"default_epsilon_choice={DEFAULT_EPSILON_CHOICE}")
    print(f"default_epsilon_collapse={DEFAULT_EPSILON_COLLAPSE}")
    print("graph_checkpoints=every_step")
    print(f"graph_chunk_size={args.graph_chunk_size}")
    print(f"run_dir={telemetry.artifact_layout.run_dir.as_posix()}")

    if args.skip_visuals:
        print("visualization=skipped")
        return 0

    if args.surface in (SURFACE_MODE_BEHAVIOR, SURFACE_MODE_ALL):
        visual_layout = build_run_visualization_layout(telemetry.artifact_layout)
        render_run_visual_bundle(
            pack,
            layout=visual_layout,
            observables=DEFAULT_GRCV3_RUN_OBSERVABLES,
        )
        print(f"visual_dir={visual_layout.run_dir.as_posix()}")
    if args.surface in (SURFACE_MODE_GRAPH, SURFACE_MODE_ALL):
        graph_layout = build_graph_run_visualization_layout(telemetry.artifact_layout)
        render_graph_run_visual_bundle(pack, layout=graph_layout)
        print(f"graph_dir={graph_layout.run_dir.as_posix()}")
    print(f"surface={args.surface}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
