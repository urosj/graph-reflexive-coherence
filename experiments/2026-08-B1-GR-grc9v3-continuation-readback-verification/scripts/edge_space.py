"""Native inverse-conductance edge metric and cycle-space projector."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def cycle_basis(
    incidence: NDArray[np.float64],
    *,
    rank_tolerance: float = 1e-12,
) -> NDArray[np.float64]:
    """Return an orthonormal edge-coordinate basis for ker(B)."""

    incidence = np.asarray(incidence, dtype=float)
    if incidence.ndim != 2:
        raise ValueError("incidence must be 2-D")
    _, singular_values, right_vectors = np.linalg.svd(incidence, full_matrices=True)
    scale = max(1.0, float(np.max(singular_values, initial=0.0)))
    rank = int(np.sum(singular_values > float(rank_tolerance) * scale))
    return np.asarray(right_vectors[rank:].T, dtype=float)


def weighted_cycle_projector(
    incidence: NDArray[np.float64],
    conductance: NDArray[np.float64],
    *,
    condition_limit: float = 1e10,
    rank_tolerance: float = 1e-12,
) -> NDArray[np.float64]:
    incidence = np.asarray(incidence, dtype=float)
    conductance = np.asarray(conductance, dtype=float)
    if incidence.ndim != 2 or conductance.ndim != 1:
        raise ValueError("incidence must be 2-D and conductance must be 1-D")
    if incidence.shape[1] != conductance.size:
        raise ValueError("one conductance is required per edge")
    if np.any(~np.isfinite(conductance)) or np.any(conductance <= 0.0):
        raise ValueError("native inverse-conductance metric requires finite positive W")
    basis = cycle_basis(incidence, rank_tolerance=rank_tolerance)
    if basis.shape[1] == 0:
        return np.zeros((conductance.size, conductance.size), dtype=float)
    metric = np.diag(1.0 / conductance)
    gram = basis.T @ metric @ basis
    condition = float(np.linalg.cond(gram))
    if not np.isfinite(condition) or condition > float(condition_limit):
        raise ValueError("cycle Gram matrix exceeds preregistered condition limit")
    return basis @ np.linalg.solve(gram, basis.T @ metric)


def projector_diagnostics(
    incidence: NDArray[np.float64],
    conductance: NDArray[np.float64],
    projector: NDArray[np.float64],
) -> dict[str, float]:
    metric = np.diag(1.0 / np.asarray(conductance, dtype=float))
    potential = np.eye(projector.shape[0]) - projector
    return {
        "idempotence_error": float(
            np.linalg.norm(projector @ projector - projector, ord=2)
        ),
        "cycle_annihilation_error": float(np.linalg.norm(incidence @ projector, ord=2)),
        "metric_self_adjointness_error": float(
            np.linalg.norm(projector.T @ metric - metric @ projector, ord=2)
        ),
        "metric_cycle_potential_orthogonality_error": float(
            np.linalg.norm(projector.T @ metric @ potential, ord=2)
        ),
        "decomposition_reconstruction_error": float(
            np.linalg.norm(projector + potential - np.eye(projector.shape[0]), ord=2)
        ),
    }


def native_potential_flow_annihilation_error(
    incidence: NDArray[np.float64],
    conductance: NDArray[np.float64],
    projector: NDArray[np.float64],
    potential: NDArray[np.float64],
    *,
    eta: float,
) -> float:
    flow = (
        -float(eta)
        * np.diag(np.asarray(conductance, dtype=float))
        @ np.asarray(incidence, dtype=float).T
        @ np.asarray(potential, dtype=float)
    )
    return float(np.linalg.norm(projector @ flow, ord=2))
