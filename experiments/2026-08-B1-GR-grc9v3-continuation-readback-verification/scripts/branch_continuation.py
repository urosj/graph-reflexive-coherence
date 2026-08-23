"""Deterministic branch and spectral-cluster matching for B1-GR."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Any, Iterable, Sequence

import numpy as np


FIRST_EXECUTABLE_GATE = "GRV2"


@dataclass(frozen=True)
class BranchCandidate:
    candidate_id: str
    residual: float
    parameter_identity: str


def select_candidate(candidates: Iterable[BranchCandidate]) -> BranchCandidate:
    rows = list(candidates)
    if not rows:
        raise ValueError("selection requires complete nonempty candidate accounting")
    return min(rows, key=lambda row: (row.residual, row.parameter_identity, row.candidate_id))


def continuation_parameter_delta(
    previous: dict[str, float], current: dict[str, float]
) -> dict[str, float]:
    """Return absolute axis deltas without silently normalizing unlike units."""

    if set(previous) != set(current):
        raise ValueError("continuation points must expose identical parameter axes")
    return {key: abs(float(current[key]) - float(previous[key])) for key in sorted(current)}


def branch_match_record(
    *,
    previous_nodes: Sequence[int],
    current_nodes: Sequence[int],
    previous_edges: Sequence[int],
    current_edges: Sequence[int],
    previous_coherence: Sequence[float],
    current_coherence: Sequence[float],
    previous_total: float,
    current_total: float,
    maximum_state_l2: float,
    maximum_total_delta: float,
) -> dict[str, Any]:
    """Apply the preregistered same-branch invariant between adjacent points."""

    left = np.asarray(previous_coherence, dtype=float)
    right = np.asarray(current_coherence, dtype=float)
    if left.shape != right.shape:
        state_l2 = float("inf")
    else:
        state_l2 = float(np.linalg.norm(right - left))
    topology_equal = bool(
        list(previous_nodes) == list(current_nodes)
        and list(previous_edges) == list(current_edges)
    )
    total_delta = abs(float(current_total) - float(previous_total))
    passed = bool(
        topology_equal
        and state_l2 <= float(maximum_state_l2)
        and total_delta <= float(maximum_total_delta)
    )
    return {
        "topology_equal": topology_equal,
        "coherence_state_l2": state_l2,
        "maximum_coherence_state_l2": float(maximum_state_l2),
        "total_coherence_delta": total_delta,
        "maximum_total_coherence_delta": float(maximum_total_delta),
        "passed": passed,
        "decision": "same_branch_matched" if passed else "branch_match_failed_closed",
    }


def real_invariant_clusters(
    eigenvalues: Sequence[complex], *, complex_pair_tolerance: float
) -> list[dict[str, Any]]:
    """Group real modes and conjugate pairs without relying on eigenvalue indices."""

    values = [complex(value) for value in eigenvalues]
    used: set[int] = set()
    clusters: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        if index in used:
            continue
        if abs(value.imag) <= complex_pair_tolerance:
            used.add(index)
            members = [complex(value.real, 0.0)]
            kind = "real_invariant_direction"
        else:
            candidates = [
                other
                for other, candidate in enumerate(values)
                if other not in used
                and other != index
                and abs(candidate - value.conjugate()) <= complex_pair_tolerance
            ]
            if not candidates:
                used.add(index)
                members = [value]
                kind = "unresolved_complex_mode"
            else:
                partner = min(candidates)
                used.update((index, partner))
                members = sorted((value, values[partner]), key=lambda item: (item.imag, item.real))
                kind = "complex_conjugate_invariant_plane"
        centroid = sum(members) / len(members)
        clusters.append(
            {
                "kind": kind,
                "dimension": len(members),
                "members": members,
                "centroid": centroid,
            }
        )
    return sorted(
        clusters,
        key=lambda row: (
            row["dimension"],
            float(row["centroid"].real),
            float(row["centroid"].imag),
        ),
    )


def match_real_invariant_clusters(
    previous: Sequence[complex],
    current: Sequence[complex],
    *,
    complex_pair_tolerance: float,
    maximum_centroid_distance: float,
) -> dict[str, Any]:
    """Match real invariant clusters by dimension and minimum centroid distance."""

    left = real_invariant_clusters(
        previous, complex_pair_tolerance=complex_pair_tolerance
    )
    right = real_invariant_clusters(
        current, complex_pair_tolerance=complex_pair_tolerance
    )
    if len(left) != len(right):
        return {
            "passed": False,
            "decision": "cluster_count_changed",
            "matches": [],
            "previous_cluster_count": len(left),
            "current_cluster_count": len(right),
        }
    best: tuple[float, tuple[int, ...]] | None = None
    for assignment in permutations(range(len(right))):
        if any(left[index]["dimension"] != right[target]["dimension"] for index, target in enumerate(assignment)):
            continue
        cost = sum(
            abs(left[index]["centroid"] - right[target]["centroid"])
            for index, target in enumerate(assignment)
        )
        candidate = (float(cost), assignment)
        if best is None or candidate < best:
            best = candidate
    if best is None:
        return {
            "passed": False,
            "decision": "cluster_dimension_changed",
            "matches": [],
            "previous_cluster_count": len(left),
            "current_cluster_count": len(right),
        }
    _, assignment = best
    matches = []
    for index, target in enumerate(assignment):
        distance = float(abs(left[index]["centroid"] - right[target]["centroid"]))
        matches.append(
            {
                "previous_cluster_index": index,
                "current_cluster_index": target,
                "dimension": left[index]["dimension"],
                "centroid_distance": distance,
                "within_declared_distance": distance <= maximum_centroid_distance,
            }
        )
    passed = all(row["within_declared_distance"] for row in matches)
    return {
        "passed": passed,
        "decision": "clusters_matched" if passed else "cluster_distance_exceeded",
        "matching_method": "minimum_total_centroid_distance_with_dimension_preservation",
        "maximum_centroid_distance": float(maximum_centroid_distance),
        "matches": matches,
        "previous_cluster_count": len(left),
        "current_cluster_count": len(right),
    }


def classify_discrete_spectrum(
    eigenvalues: Sequence[complex],
    *,
    threshold_tolerance: float,
    complex_imaginary_floor: float,
) -> dict[str, Any]:
    """Classify declared +1, stable, -1, complex-unit, and unstable surfaces."""

    values = [complex(value) for value in eigenvalues]
    if not values:
        return {
            "status": "not_available",
            "aggregate_classification": "not_available",
            "plus_one_reached": False,
            "minus_one_reached": False,
            "stable_interior_reached": False,
            "complex_unit_circle_reached": False,
            "unstable_reached": False,
            "modes": [],
        }
    modes = []
    for value in values:
        magnitude = abs(value)
        plus_distance = abs(value - 1.0)
        minus_distance = abs(value + 1.0)
        complex_unit = bool(
            abs(value.imag) >= complex_imaginary_floor
            and abs(magnitude - 1.0) <= threshold_tolerance
        )
        if plus_distance <= threshold_tolerance:
            classification = "plus_one_marginality"
        elif minus_distance <= threshold_tolerance:
            classification = "minus_one_flip_marginality"
        elif complex_unit:
            classification = "complex_unit_circle_marginality"
        elif magnitude < 1.0 - threshold_tolerance:
            classification = "stable_interior"
        elif magnitude > 1.0 + threshold_tolerance:
            classification = "unstable_exterior"
        else:
            classification = "unit_circle_near_marginal"
        modes.append(
            {
                "real": float(value.real),
                "imag": float(value.imag),
                "magnitude": float(magnitude),
                "distance_to_plus_one": float(plus_distance),
                "distance_to_minus_one": float(minus_distance),
                "unit_circle_distance": float(abs(magnitude - 1.0)),
                "classification": classification,
            }
        )
    labels = {row["classification"] for row in modes}
    if "unstable_exterior" in labels:
        aggregate = "unstable_exterior"
    elif labels == {"stable_interior"}:
        aggregate = "stable_interior"
    elif "minus_one_flip_marginality" in labels:
        aggregate = "minus_one_flip_marginality"
    elif "complex_unit_circle_marginality" in labels:
        aggregate = "complex_unit_circle_marginality"
    elif "plus_one_marginality" in labels:
        aggregate = "plus_one_marginality"
    else:
        aggregate = "mixed_or_near_marginal"
    return {
        "status": "classified",
        "aggregate_classification": aggregate,
        "plus_one_reached": "plus_one_marginality" in labels,
        "minus_one_reached": "minus_one_flip_marginality" in labels,
        "stable_interior_reached": "stable_interior" in labels,
        "complex_unit_circle_reached": "complex_unit_circle_marginality" in labels,
        "unstable_reached": "unstable_exterior" in labels,
        "modes": modes,
    }
