"""Native inverse-conductance edge metric and cycle-space projector."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def weighted_cycle_projector(
    incidence: NDArray[np.float64],
    conductance: NDArray[np.float64],
    *,
    condition_limit: float = 1e10,
) -> NDArray[np.float64]:
    incidence = np.asarray(incidence, dtype=float)
    conductance = np.asarray(conductance, dtype=float)
    if incidence.ndim != 2 or conductance.ndim != 1:
        raise ValueError("incidence must be 2-D and conductance must be 1-D")
    if incidence.shape[1] != conductance.size:
        raise ValueError("one conductance is required per edge")
    if np.any(~np.isfinite(conductance)) or np.any(conductance <= 0.0):
        raise ValueError("native inverse-conductance metric requires finite positive W")
    weighted_laplacian = incidence @ np.diag(conductance) @ incidence.T
    nonzero = np.linalg.eigvalsh(weighted_laplacian)
    nonzero = nonzero[nonzero > np.finfo(float).eps * max(1.0, np.max(np.abs(nonzero)))]
    if nonzero.size and float(np.max(nonzero) / np.min(nonzero)) > condition_limit:
        raise ValueError("weighted incidence system exceeds preregistered condition limit")
    return np.eye(conductance.size) - (
        np.diag(conductance)
        @ incidence.T
        @ np.linalg.pinv(weighted_laplacian)
        @ incidence
    )


def projector_diagnostics(
    incidence: NDArray[np.float64],
    conductance: NDArray[np.float64],
    projector: NDArray[np.float64],
) -> dict[str, float]:
    metric = np.diag(1.0 / np.asarray(conductance, dtype=float))
    return {
        "idempotence_error": float(np.linalg.norm(projector @ projector - projector, ord=2)),
        "cycle_annihilation_error": float(np.linalg.norm(incidence @ projector, ord=2)),
        "metric_self_adjointness_error": float(np.linalg.norm(projector.T @ metric - metric @ projector, ord=2)),
    }
