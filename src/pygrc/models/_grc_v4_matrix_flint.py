"""Native exact FLINT matrix kernels for the selected V4 CPU backend."""

from __future__ import annotations

from typing import TypeAlias, cast

from flint import fmpq, fmpq_mat  # type: ignore[import-not-found]

from .grc_v4_exact import ExactScalar

ExactMatrix: TypeAlias = tuple[tuple[ExactScalar, ...], ...]


def matmul(left: ExactMatrix, right: ExactMatrix) -> ExactMatrix:
    return cast(ExactMatrix, tuple(tuple(row) for row in (fmpq_mat(left) * fmpq_mat(right)).tolist()))


def inverse(matrix: ExactMatrix) -> ExactMatrix:
    return cast(ExactMatrix, tuple(tuple(row) for row in fmpq_mat(matrix).inv().tolist()))


def positive_semidefinite(matrix: ExactMatrix) -> bool:
    """Exact Schur-complement decision, identical to the Python algorithm."""
    rows = [list(row) for row in matrix]
    while rows:
        n = len(rows)
        pivot = next((i for i in range(n) if rows[i][i] > 0), None)
        if pivot is None:
            return not any(value for row in rows for value in row)
        if pivot:
            order = [pivot] + [i for i in range(n) if i != pivot]
            rows = [[rows[i][j] for j in order] for i in order]
        diagonal = rows[0][0]
        size = n - 1
        reduced = [[fmpq(0)] * size for _ in range(size)]
        for i in range(size):
            gain = rows[i + 1][0] / diagonal
            for j in range(i, size):
                value = rows[i + 1][j + 1] - gain * rows[j + 1][0]
                reduced[i][j] = reduced[j][i] = value
        rows = reduced
    return True
