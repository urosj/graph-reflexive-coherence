"""Zero-sum coherence tangent bases used by B1-GR."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def zero_sum_basis(size: int) -> NDArray[np.float64]:
    if size < 2:
        raise ValueError("zero-sum tangent requires at least two nodes")
    matrix = np.zeros((size, size - 1), dtype=float)
    for column in range(size - 1):
        scale = np.sqrt((column + 1) * (column + 2))
        matrix[: column + 1, column] = 1.0 / scale
        matrix[column + 1, column] = -(column + 1) / scale
    return matrix


def basis_checks(basis: NDArray[np.float64]) -> dict[str, float]:
    size, columns = basis.shape
    identity_error = float(np.linalg.norm(basis.T @ basis - np.eye(columns), ord=2))
    zero_sum_error = float(np.linalg.norm(np.ones((1, size)) @ basis, ord=2))
    return {"orthonormality_error": identity_error, "zero_sum_error": zero_sum_error}
