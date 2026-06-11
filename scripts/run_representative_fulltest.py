"""Rebuild the canonical dense representative fulltest artifacts.

This script reproduces the artifact envelope used for the dense fulltest lanes:

- seeds: `cell-1` and `cell-4`
- steps: `100`
- graph checkpoints: every step
- graph checkpoint chunk size: `25`
- flow overlays: enabled
- visualization surface: `all` by default

Family-specific defaults:

- `grcv2`
  - parameter family: `balanced_baseline`
  - RNG seed: `7`
  - artifact path: `outputs/<experiment_id>/grcv2/...`
- `grcv3`
  - profile: `seed_baseline`
  - artifact path: `outputs/<experiment_id>/grcv3/<profile>/...`

The script writes artifacts under `outputs/<experiment_id>/...` so the caller
can either reconstruct the canonical lane or generate a new side-by-side rerun
under a different experiment id.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.telemetry import (
    DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    run_grcv2_representative_experiment,
    run_grcv3_landscape_experiment,
)
from pygrc.visualization import (
    SUPPORTED_SURFACE_MODES,
    render_grcv2_representative_visual_suite,
    render_grcv3_landscape_visual_suite,
)


DEFAULT_OUTPUTS_ROOT = Path("outputs")
DEFAULT_EXPERIMENT_ID = "representative-fulltest"
DEFAULT_MODEL_FAMILY = "grcv2"
DEFAULT_GRCV2_FAMILY_NAME = "balanced_baseline"
DEFAULT_GRCV3_PROFILE_NAME = DEFAULT_GRCV3_LANDSCAPE_PROFILE
DEFAULT_STEPS = 100
DEFAULT_RNG_SEED = 7
DEFAULT_GRAPH_CHUNK_SIZE = 25
DEFAULT_SURFACE_MODE = "all"
SUPPORTED_MODEL_FAMILIES = ("grcv2", "grcv3")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the canonical dense representative fulltest for GRCV2 or "
            "GRCV3 and, by default, render the matching visualization suite."
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
        "--model-family",
        choices=SUPPORTED_MODEL_FAMILIES,
        default=DEFAULT_MODEL_FAMILY,
        help="Which family-specific fulltest lane to run.",
    )
    parser.add_argument(
        "--family",
        default=DEFAULT_GRCV2_FAMILY_NAME,
        help="Representative GRCV2 parameter family.",
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_GRCV3_PROFILE_NAME,
        help="Seed-driven GRCV3 landscape profile.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of model steps per seed.",
    )
    parser.add_argument(
        "--rng-seed",
        type=int,
        default=DEFAULT_RNG_SEED,
        help="Deterministic RNG seed for the GRCV2 representative lane.",
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


def _run_grcv2_fulltest(args: argparse.Namespace, outputs_root: Path) -> int:
    experiment_path = Path(args.experiment_id) / "grcv2"

    result = run_grcv2_representative_experiment(
        telemetry_root=outputs_root,
        telemetry_experiment_path=experiment_path,
        family_name=args.family,
        num_steps=args.steps,
        rng_seed=args.rng_seed,
        record_graph_checkpoints=True,
        checkpoint_every_step=True,
        checkpoint_chunk_size=args.graph_chunk_size,
        include_flow_overlays=True,
    )

    assert result.cell1_run.telemetry is not None
    assert result.cell4_run.telemetry is not None
    cell1_layout = result.cell1_run.telemetry.artifact_layout
    cell4_layout = result.cell4_run.telemetry.artifact_layout

    print("Representative fulltest telemetry complete.")
    print("model_family=grcv2")
    print(f"experiment_id={args.experiment_id}")
    print(f"family={result.family_name}")
    print(f"steps={result.num_steps}")
    print(f"rng_seed={result.rng_seed}")
    print("graph_checkpoints=every_step")
    print(f"graph_chunk_size={args.graph_chunk_size}")
    if cell1_layout is not None:
        print(f"cell-1 run_dir={cell1_layout.run_dir.as_posix()}")
    if cell4_layout is not None:
        print(f"cell-4 run_dir={cell4_layout.run_dir.as_posix()}")

    if args.skip_visuals:
        print("visualization=skipped")
        return 0

    visual_result = render_grcv2_representative_visual_suite(
        telemetry_root=outputs_root,
        telemetry_experiment_path=experiment_path,
        family_name=args.family,
        surface_mode=args.surface,
    )
    print("Representative fulltest visualization complete.")
    print(f"surface={visual_result.surface_mode}")
    print(
        "cell-1 visual_dir="
        + visual_result.cell1_visualization_layout.run_dir.as_posix()
    )
    print(
        "cell-4 visual_dir="
        + visual_result.cell4_visualization_layout.run_dir.as_posix()
    )
    print(
        "comparison_dir="
        + visual_result.comparison_visualization_layout.comparison_dir.as_posix()
    )
    if visual_result.cell1_graph_visualization_layout is not None:
        print(
            "cell-1 graph_dir="
            + visual_result.cell1_graph_visualization_layout.run_dir.as_posix()
        )
    if visual_result.cell4_graph_visualization_layout is not None:
        print(
            "cell-4 graph_dir="
            + visual_result.cell4_graph_visualization_layout.run_dir.as_posix()
        )
    if visual_result.graph_comparison_visualization_layout is not None:
        print(
            "graph_comparison_dir="
            + visual_result.graph_comparison_visualization_layout.comparison_dir.as_posix()
        )
    return 0


def _run_grcv3_fulltest(args: argparse.Namespace, outputs_root: Path) -> int:
    experiment_path = Path(args.experiment_id) / "grcv3"

    result = run_grcv3_landscape_experiment(
        telemetry_root=outputs_root,
        telemetry_experiment_path=experiment_path,
        profile_name=args.profile,
        num_steps=args.steps,
        record_graph_checkpoints=True,
        checkpoint_every_step=True,
        checkpoint_chunk_size=args.graph_chunk_size,
        include_flow_overlays=True,
    )

    assert result.cell1_run.telemetry is not None
    assert result.cell4_run.telemetry is not None
    cell1_layout = result.cell1_run.telemetry.artifact_layout
    cell4_layout = result.cell4_run.telemetry.artifact_layout

    print("Representative fulltest telemetry complete.")
    print("model_family=grcv3")
    print(f"experiment_id={args.experiment_id}")
    print(f"profile={result.profile_name}")
    print(f"steps={result.num_steps}")
    print("graph_checkpoints=every_step")
    print(f"graph_chunk_size={args.graph_chunk_size}")
    if cell1_layout is not None:
        print(f"cell-1 run_dir={cell1_layout.run_dir.as_posix()}")
    if cell4_layout is not None:
        print(f"cell-4 run_dir={cell4_layout.run_dir.as_posix()}")

    if args.skip_visuals:
        print("visualization=skipped")
        return 0

    visual_result = render_grcv3_landscape_visual_suite(
        telemetry_root=outputs_root,
        telemetry_experiment_path=experiment_path,
        profile_name=args.profile,
        surface_mode=args.surface,
    )
    print("Representative fulltest visualization complete.")
    print(f"surface={visual_result.surface_mode}")
    print(
        "cell-1 visual_dir="
        + visual_result.cell1_visualization_layout.run_dir.as_posix()
    )
    print(
        "cell-4 visual_dir="
        + visual_result.cell4_visualization_layout.run_dir.as_posix()
    )
    print(
        "comparison_dir="
        + visual_result.comparison_visualization_layout.comparison_dir.as_posix()
    )
    if visual_result.cell1_graph_visualization_layout is not None:
        print(
            "cell-1 graph_dir="
            + visual_result.cell1_graph_visualization_layout.run_dir.as_posix()
        )
    if visual_result.cell4_graph_visualization_layout is not None:
        print(
            "cell-4 graph_dir="
            + visual_result.cell4_graph_visualization_layout.run_dir.as_posix()
        )
    if visual_result.graph_comparison_visualization_layout is not None:
        print(
            "graph_comparison_dir="
            + visual_result.graph_comparison_visualization_layout.comparison_dir.as_posix()
        )
    return 0


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    outputs_root = Path(args.outputs_root)
    if args.model_family == "grcv2":
        return _run_grcv2_fulltest(args, outputs_root)
    if args.model_family == "grcv3":
        return _run_grcv3_fulltest(args, outputs_root)
    raise AssertionError(f"unsupported model family: {args.model_family}")


if __name__ == "__main__":
    raise SystemExit(main())
