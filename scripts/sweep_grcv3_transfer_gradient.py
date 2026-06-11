#!/usr/bin/env python3
"""Run a narrow transfer-focused diagnostic around the best current rich-v3 probe.

This is intentionally smaller than the first softness sweep:

- fixed source geometry
- fixed carrier layout
- vary only carrier-to-probe transfer remapping

The question is whether transfer semantics can reduce center gradient enough
without giving back the signed-Hessian progress already recovered.
"""

from __future__ import annotations

import argparse
import copy
import math
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.landscapes import BasinSeedPrimitive, LandscapeSeed, load_landscape_seed
from pygrc.models import build_grcv3_from_landscape_seed, resolve_grcv3_landscape_params
from pygrc.models.grc_v3_differential import symmetric_eigenvalues


DEFAULT_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml"
)
DEFAULT_PROFILE = "seed_baseline"
DEFAULT_STEPS = 50
_CORE_PRIMITIVE_ID = "spindle_core"


@dataclass(frozen=True)
class TransferPreset:
    name: str
    transfer_topology_mode: str
    transfer_role_pairs: tuple[tuple[str, str], ...]


TRANSFER_PRESETS = (
    TransferPreset(
        name="identity_group_bridge",
        transfer_topology_mode="group_bridge",
        transfer_role_pairs=(
            ("north", "north"),
            ("south", "south"),
            ("east", "east"),
            ("west", "west"),
        ),
    ),
    TransferPreset(
        name="weak_to_stable_bridge",
        transfer_topology_mode="paired_role_bridge",
        transfer_role_pairs=(
            ("north", "north"),
            ("south", "south"),
            ("east", "north"),
            ("west", "south"),
        ),
    ),
    TransferPreset(
        name="stable_to_weak_bridge",
        transfer_topology_mode="paired_role_bridge",
        transfer_role_pairs=(
            ("north", "east"),
            ("south", "west"),
            ("east", "east"),
            ("west", "west"),
        ),
    ),
    TransferPreset(
        name="cross_swap_bridge",
        transfer_topology_mode="paired_role_bridge",
        transfer_role_pairs=(
            ("north", "south"),
            ("south", "north"),
            ("east", "north"),
            ("west", "south"),
        ),
    ),
)


def _core_primitive(seed: LandscapeSeed) -> BasinSeedPrimitive:
    for primitive in seed.primitives:
        if primitive.id == _CORE_PRIMITIVE_ID:
            if not isinstance(primitive, BasinSeedPrimitive):
                raise TypeError(f"{_CORE_PRIMITIVE_ID!r} must remain a basin primitive")
            return primitive
    raise KeyError(f"seed has no {_CORE_PRIMITIVE_ID!r} primitive")


def _gradient_norm(values: list[float]) -> float:
    return math.sqrt(sum(float(value) * float(value) for value in values))


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a narrow transfer-focused GRCV3 rich-v3 diagnostic sweep."
    )
    parser.add_argument(
        "--seed",
        default=str(DEFAULT_SEED),
        help="Relative path to the weak-to-stable rich-v3 probe seed.",
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        help="Landscape profile name resolved before building the model.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of GRCV3 steps per transfer preset.",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    base_seed = load_landscape_seed(Path(args.seed))
    print(
        "GRCV3 transfer-focused sweep "
        f"(seed={args.seed}, profile={args.profile}, steps={args.steps})"
    )
    print("thresholds: eps_gradient=0.001 eps_hessian=0.001 eps_spark=0.001")
    print()

    for preset in TRANSFER_PRESETS:
        seed = copy.deepcopy(base_seed)
        core = _core_primitive(seed)
        carriers = core.extensions["grcv3"]["interior_load_carriers"]
        carriers["transfer_topology_mode"] = preset.transfer_topology_mode
        carriers["transfer_role_pairs"] = [
            [carrier_role, probe_role]
            for carrier_role, probe_role in preset.transfer_role_pairs
        ]

        params = resolve_grcv3_landscape_params(seed, profile_name=args.profile)
        model = build_grcv3_from_landscape_seed(
            seed,
            params=params,
            profile_name=args.profile,
            validate_seed=False,
        )
        spark_events = 0
        spark_candidates = 0
        for _ in range(args.steps):
            result = model.step()
            for event in result.events:
                if event.kind == "spark":
                    spark_events += 1
                elif event.kind == "spark_candidate":
                    spark_candidates += 1

        state = model.get_state()
        center_node_id = state.cached_quantities["landscape_node_id_by_primitive_id"][
            _CORE_PRIMITIVE_ID
        ]
        attrs = state.nodes[center_node_id]
        hessian_sign = int(state.cached_quantities["hessian_sign"])
        signed_hessian = [
            [hessian_sign * float(value) for value in row]
            for row in attrs.hessian
        ]
        signed_eigenvalues = tuple(
            sorted(float(value) for value in symmetric_eigenvalues(signed_hessian))
        )
        observables = model.compute_observables()
        stable_axis = signed_eigenvalues[1] if len(signed_eigenvalues) > 1 else float("nan")
        weak_axis = signed_eigenvalues[0] if signed_eigenvalues else float("nan")
        print(preset.name)
        print(
            "  "
            f"grad={_gradient_norm(attrs.gradient):.12g} "
            f"weak={weak_axis:.12g} "
            f"stable={stable_axis:.12g} "
            f"seed_count={observables.get('geometric_seed_count')} "
            f"validated={observables.get('geometric_validated_basin_count')} "
            f"spark_candidates={spark_candidates} "
            f"sparks={spark_events}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
