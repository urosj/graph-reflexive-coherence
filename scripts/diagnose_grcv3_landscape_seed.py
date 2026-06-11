#!/usr/bin/env python3
"""Short diagnostic gate for seed-driven GRCV3 landscape projections."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pygrc.models import build_grcv3_from_landscape_seed, resolve_grcv3_landscape_params
from pygrc.models.grc_v3 import symmetric_eigenvalues


def _gradient_norm(values: list[float]) -> float:
    return sum(value * value for value in values) ** 0.5


def _rows_for_state(model: Any) -> list[dict[str, Any]]:
    state = model.get_state()
    hessian_sign = int(state.cached_quantities["hessian_sign"])
    rows: list[dict[str, Any]] = []
    for node_id in sorted(state.topology.iter_live_node_ids()):
        attributes = state.nodes[node_id]
        payload = state.topology.node_payload(node_id)
        signed_hessian = [
            [hessian_sign * float(value) for value in row]
            for row in attributes.hessian
        ]
        eigenvalues = symmetric_eigenvalues(signed_hessian) if signed_hessian else []
        rows.append(
            {
                "node_id": node_id,
                "primitive_id": payload.get("primitive_id"),
                "motif_role": payload.get("motif_role"),
                "gradient_norm": _gradient_norm(attributes.gradient),
                "signed_eigenvalues": [float(value) for value in eigenvalues],
            }
        )
    return rows


def _run_pre_spark_sequence(model: Any) -> dict[str, Any]:
    model.rebuild_basin_attributes()
    model._compute_node_tensors()
    model._compute_metric()
    model._compute_edge_labels(pre_flux_only=True)
    model._compute_potential()
    model._compute_flux()
    model._compute_edge_labels(pre_flux_only=False)
    model.rebuild_basin_attributes()
    model.rebuild_identity_state()

    state = model.get_state()
    geometric_identity = dict(state.cached_quantities.get("geometric_identity", {}))
    spark_candidates = model.detect_spark_candidates()
    return {
        "geometric_identity": geometric_identity,
        "spark_candidates": spark_candidates,
        "rows": _rows_for_state(model),
    }


def _print_rows(rows: list[dict[str, Any]], *, limit: int, heading: str) -> None:
    print(heading)
    for row in rows[:limit]:
        print(
            "  "
            f"node={row['node_id']} "
            f"primitive={row['primitive_id']} "
            f"role={row['motif_role']} "
            f"grad={row['gradient_norm']:.12g} "
            f"eig={row['signed_eigenvalues']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the short GRCV3 landscape diagnostic gate for one seed."
    )
    parser.add_argument(
        "seed",
        nargs="?",
        default="configs/landscapes/seed/cell-4.seed.yaml",
        help="Relative path to the landscape seed.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=5,
        help="Number of short runtime steps to inspect after the pre-spark gate.",
    )
    parser.add_argument(
        "--profile",
        default="seed_baseline",
        help="GRCV3 landscape profile name to resolve before building the model.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=12,
        help="Maximum number of diagnostic rows to print per section.",
    )
    args = parser.parse_args()

    seed_path = Path(args.seed)
    params = resolve_grcv3_landscape_params(seed_path, profile_name=args.profile)

    model = build_grcv3_from_landscape_seed(seed_path, params=params)
    state = model.get_state()
    print("INITIAL")
    print(
        "  "
        f"seed={seed_path} "
        f"profile={args.profile} "
        f"nodes={len(tuple(state.topology.iter_live_node_ids()))} "
        f"edges={len(tuple(state.topology.iter_live_edge_ids()))}"
    )
    print(f"  observables={model.compute_observables()}")
    print(
        "  thresholds="
        f"{{'eps_gradient': {params.evolution['eps_gradient']}, "
        f"'eps_hessian': {params.evolution['eps_hessian']}, "
        f"'eps_spark': {params.evolution['eps_spark']}}}"
    )

    pre_spark = _run_pre_spark_sequence(model)
    geometric_identity = pre_spark["geometric_identity"]
    rows = pre_spark["rows"]
    print("PRE-SPARK")
    print(f"  seed_nodes={geometric_identity.get('seed_nodes', [])}")
    print(f"  validated_basin_ids={geometric_identity.get('validated_basin_ids', [])}")
    print(f"  spark_candidates={len(pre_spark['spark_candidates'])}")
    if pre_spark["spark_candidates"]:
        for event in pre_spark["spark_candidates"][: args.limit]:
            print(f"  candidate={event.payload}")
    _print_rows(
        sorted(rows, key=lambda row: (row["gradient_norm"], row["node_id"])),
        limit=args.limit,
        heading="LOWEST-GRADIENT NODES",
    )
    eps_gradient = float(params.evolution["eps_gradient"])
    low_gradient_rows = [row for row in rows if row["gradient_norm"] < eps_gradient]
    _print_rows(
        sorted(
            low_gradient_rows,
            key=lambda row: (
                min(row["signed_eigenvalues"]) if row["signed_eigenvalues"] else float("inf"),
                row["node_id"],
            ),
        ),
        limit=args.limit,
        heading="LOW-GRADIENT CANDIDATES ORDERED BY WEAKEST SIGNED EIGENVALUE",
    )

    print("SHORT-RUN")
    model = build_grcv3_from_landscape_seed(seed_path, params=params)
    for step_index in range(1, args.steps + 1):
        result = model.step()
        state = model.get_state()
        geometric_identity = dict(state.cached_quantities.get("geometric_identity", {}))
        candidates = model.detect_spark_candidates()
        print(
            "  "
            f"step={step_index} "
            f"geometric_seed_count={result.observables.get('geometric_seed_count')} "
            f"validated_basin_count={result.observables.get('geometric_validated_basin_count')} "
            f"spark_event_count={result.observables.get('spark_event_count')} "
            f"candidate_count={len(candidates)}"
        )
        print(f"    seed_nodes={geometric_identity.get('seed_nodes', [])}")
        if candidates:
            for event in candidates[: args.limit]:
                print(f"    candidate={event.payload}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
