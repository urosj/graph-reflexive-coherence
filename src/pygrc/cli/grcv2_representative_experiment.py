"""Run the canonical telemetry-backed GRCV2 representative experiment."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from pygrc.telemetry import (
    DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_REPRESENTATIVE_FAMILY,
    DEFAULT_REPRESENTATIVE_RNG_SEED,
    DEFAULT_REPRESENTATIVE_STEPS,
    DEFAULT_TELEMETRY_ROOT,
    run_grcv2_representative_experiment,
)


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the representative `GRCV2` experiment lane."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the canonical GRCV2 representative experiment for cell-1 and "
            "cell-4, emitting telemetry/report artifacts under outputs/. "
            "This command records the behavior-facing telemetry lane only; "
            "graph checkpoint export remains opt-in through the programmatic API "
            "or future explicit graph flags."
        )
    )
    parser.add_argument(
        "--telemetry-root",
        default=str(DEFAULT_TELEMETRY_ROOT),
        help="Project-relative root under which experiment artifacts are written.",
    )
    parser.add_argument(
        "--experiment-path",
        default=str(DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH),
        help="Relative experiment lane under the telemetry root.",
    )
    parser.add_argument(
        "--family",
        default=DEFAULT_REPRESENTATIVE_FAMILY,
        help="Named GRCV2 parameter family to run.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_REPRESENTATIVE_STEPS,
        help="Number of model steps to execute for each seed.",
    )
    parser.add_argument(
        "--rng-seed",
        type=int,
        default=DEFAULT_REPRESENTATIVE_RNG_SEED,
        help="Deterministic RNG seed for both runs.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the representative experiment and print a concise artifact summary."""

    parser = build_argument_parser()
    args = parser.parse_args(argv)
    result = run_grcv2_representative_experiment(
        telemetry_root=Path(args.telemetry_root),
        telemetry_experiment_path=Path(args.experiment_path),
        family_name=args.family,
        num_steps=args.steps,
        rng_seed=args.rng_seed,
    )

    assert result.cell1_run.telemetry is not None
    assert result.cell4_run.telemetry is not None
    cell1_layout = result.cell1_run.telemetry.artifact_layout
    cell4_layout = result.cell4_run.telemetry.artifact_layout

    print("Representative GRCV2 experiment complete.")
    print(f"family={result.family_name} steps={result.num_steps} rng_seed={result.rng_seed}")
    if cell1_layout is not None:
        print(f"cell-1 run_dir={cell1_layout.run_dir.as_posix()}")
    if cell4_layout is not None:
        print(f"cell-4 run_dir={cell4_layout.run_dir.as_posix()}")
    print(
        "cell-1 changed_observables="
        + ",".join(result.cell1_report.common["changed_observables"])
    )
    print(
        "cell-4 changed_observables="
        + ",".join(result.cell4_report.common["changed_observables"])
    )
    print(
        "comparison_delta_keys="
        + ",".join(sorted(result.comparison_report.common["final_observables_right_minus_left"]))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
