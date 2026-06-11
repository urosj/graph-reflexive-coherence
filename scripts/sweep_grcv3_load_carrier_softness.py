#!/usr/bin/env python3
"""Run a small softness-oriented sweep around the rich-v3 load-carrier probe.

The goal is diagnostic rather than exhaustive optimization:

- keep the same source seed family
- vary only a few geometry/carrier-transfer softness knobs
- measure whether the center moves toward:
  - low gradient
  - one weak signed-Hessian axis
  - one stably positive signed-Hessian axis

This is intended as a reproducible follow-on to the first
`interior_load_carriers` near-miss.
"""

from __future__ import annotations

import argparse
import copy
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
    / "grcv3-rich-v3-load-carrier-spindle-probe.seed.yaml"
)
DEFAULT_PROFILE = "seed_baseline"
DEFAULT_STEPS = 50
_CORE_PRIMITIVE_ID = "spindle_core"


@dataclass(frozen=True)
class GeometryPreset:
    name: str
    support_profile: dict[str, str]
    interior_clearance_class: str


@dataclass(frozen=True)
class CarrierPreset:
    name: str
    carrier_layout_mode: str
    carrier_anchor_policy: str


@dataclass(frozen=True)
class TransferPreset:
    name: str
    transfer_topology_mode: str
    transfer_role_pairs: list[list[str]]


@dataclass(frozen=True)
class SweepResult:
    variant_name: str
    geometry_preset: str
    carrier_preset: str
    transfer_preset: str
    gradient_norm: float
    signed_eigenvalues: tuple[float, ...]
    geometric_seed_count: float | None
    geometric_validated_basin_count: float | None
    spark_candidate_count: int
    spark_event_count: int


GEOMETRY_PRESETS = (
    GeometryPreset(
        name="strict",
        support_profile={
            "north": "tight",
            "east": "loose",
            "south": "tight",
            "west": "loose",
        },
        interior_clearance_class="shielded",
    ),
    GeometryPreset(
        name="moderate",
        support_profile={
            "north": "neutral",
            "east": "loose",
            "south": "neutral",
            "west": "loose",
        },
        interior_clearance_class="semi_open",
    ),
    GeometryPreset(
        name="relaxed",
        support_profile={
            "north": "neutral",
            "east": "neutral",
            "south": "neutral",
            "west": "neutral",
        },
        interior_clearance_class="semi_open",
    ),
)

CARRIER_PRESETS = (
    CarrierPreset(
        name="group_midpoints",
        carrier_layout_mode="group_midpoints",
        carrier_anchor_policy="group_centroid",
    ),
    CarrierPreset(
        name="offset_ring",
        carrier_layout_mode="offset_ring",
        carrier_anchor_policy="between_roles",
    ),
    CarrierPreset(
        name="staggered_arc",
        carrier_layout_mode="staggered_arc",
        carrier_anchor_policy="group_centroid",
    ),
)

TRANSFER_PRESETS = (
    TransferPreset(
        name="identity_group_bridge",
        transfer_topology_mode="group_bridge",
        transfer_role_pairs=[
            ["north", "north"],
            ["south", "south"],
            ["east", "east"],
            ["west", "west"],
        ],
    ),
    TransferPreset(
        name="weak_to_stable_bridge",
        transfer_topology_mode="paired_role_bridge",
        transfer_role_pairs=[
            ["north", "north"],
            ["south", "south"],
            ["east", "north"],
            ["west", "south"],
        ],
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


def _analyze_variant(
    seed: LandscapeSeed,
    *,
    geometry: GeometryPreset,
    carrier: CarrierPreset,
    transfer: TransferPreset,
    profile_name: str,
    steps: int,
) -> SweepResult:
    variant_seed = copy.deepcopy(seed)
    core = _core_primitive(variant_seed)
    grcv3_extension = core.extensions["grcv3"]
    interior_geometry = grcv3_extension["interior_geometry"]
    interior_load_carriers = grcv3_extension["interior_load_carriers"]

    interior_geometry["support_profile"] = dict(geometry.support_profile)
    interior_geometry["interior_clearance_class"] = geometry.interior_clearance_class
    interior_load_carriers["carrier_layout_mode"] = carrier.carrier_layout_mode
    interior_load_carriers["carrier_anchor_policy"] = carrier.carrier_anchor_policy
    interior_load_carriers["transfer_topology_mode"] = transfer.transfer_topology_mode
    interior_load_carriers["transfer_role_pairs"] = copy.deepcopy(
        transfer.transfer_role_pairs
    )

    params = resolve_grcv3_landscape_params(variant_seed, profile_name=profile_name)
    model = build_grcv3_from_landscape_seed(
        variant_seed,
        params=params,
        profile_name=profile_name,
        validate_seed=False,
    )
    spark_event_count = 0
    spark_candidate_count = 0
    for _ in range(steps):
        result = model.step()
        for event in result.events:
            if event.kind == "spark":
                spark_event_count += 1
            elif event.kind == "spark_candidate":
                spark_candidate_count += 1

    state = model.get_state()
    center_node_id = state.cached_quantities["landscape_node_id_by_primitive_id"][
        _CORE_PRIMITIVE_ID
    ]
    attributes = state.nodes[center_node_id]
    hessian_sign = int(state.cached_quantities["hessian_sign"])
    signed_hessian = [
        [hessian_sign * float(value) for value in row]
        for row in attributes.hessian
    ]
    signed_eigenvalues = tuple(
        sorted(float(value) for value in symmetric_eigenvalues(signed_hessian))
    )
    observables = model.compute_observables()
    variant_name = (
        f"geom={geometry.name}/carrier={carrier.name}/transfer={transfer.name}"
    )
    return SweepResult(
        variant_name=variant_name,
        geometry_preset=geometry.name,
        carrier_preset=carrier.name,
        transfer_preset=transfer.name,
        gradient_norm=_gradient_norm(attributes.gradient),
        signed_eigenvalues=signed_eigenvalues,
        geometric_seed_count=observables.get("geometric_seed_count"),
        geometric_validated_basin_count=observables.get(
            "geometric_validated_basin_count"
        ),
        spark_candidate_count=spark_candidate_count,
        spark_event_count=spark_event_count,
    )


def _sort_key(result: SweepResult) -> tuple[float, float, float]:
    stable_axis = (
        result.signed_eigenvalues[1] if len(result.signed_eigenvalues) > 1 else float("-inf")
    )
    weak_axis = (
        result.signed_eigenvalues[0] if result.signed_eigenvalues else float("inf")
    )
    return (
        float(result.gradient_norm),
        -float(stable_axis),
        abs(float(weak_axis)),
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a small GRCV3 load-carrier softness sweep."
    )
    parser.add_argument(
        "--seed",
        default=str(DEFAULT_SEED),
        help="Relative path to the baseline rich-v3 load-carrier probe seed.",
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
        help="Number of GRCV3 steps per variant.",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    seed = load_landscape_seed(Path(args.seed))
    results: list[SweepResult] = []
    for geometry in GEOMETRY_PRESETS:
        for carrier in CARRIER_PRESETS:
            for transfer in TRANSFER_PRESETS:
                results.append(
                    _analyze_variant(
                        seed,
                        geometry=geometry,
                        carrier=carrier,
                        transfer=transfer,
                        profile_name=args.profile,
                        steps=args.steps,
                    )
                )

    eps_gradient = 1e-3
    eps_hessian = 1e-3
    eps_spark = 1e-3
    print(
        "GRCV3 load-carrier softness sweep "
        f"(seed={args.seed}, profile={args.profile}, steps={args.steps})"
    )
    print(
        f"thresholds: eps_gradient={eps_gradient} "
        f"eps_hessian={eps_hessian} eps_spark={eps_spark}"
    )
    print()
    for result in sorted(results, key=_sort_key):
        stable_axis = (
            result.signed_eigenvalues[1]
            if len(result.signed_eigenvalues) > 1
            else float("nan")
        )
        weak_axis = (
            result.signed_eigenvalues[0]
            if result.signed_eigenvalues
            else float("nan")
        )
        print(result.variant_name)
        print(
            "  "
            f"grad={result.gradient_norm:.12g} "
            f"weak={weak_axis:.12g} "
            f"stable={stable_axis:.12g} "
            f"seed_count={result.geometric_seed_count} "
            f"validated={result.geometric_validated_basin_count} "
            f"spark_candidates={result.spark_candidate_count} "
            f"sparks={result.spark_event_count}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
