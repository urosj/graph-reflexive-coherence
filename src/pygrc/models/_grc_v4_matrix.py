"""Private exact arithmetic implementation for the shared V4 matrix API.

Only grc_v4_numerics calls the inverse and conditioning implementations.
Legacy failure messages are preserved because they enter public receipts.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import TypeAlias

from .grc_v4_codec import _dependency
from .grc_v4_geometry import Matrix, _computed
from .grc_v4_state import SolverDisposition

ExactMatrix: TypeAlias = tuple[tuple[Fraction, ...], ...]


class MatrixError(ValueError):
    """Observed numeric failure; the operation owner supplies stage and receipt.

    Residual rejection means no numerically admitted root was produced, not
    proof that the underlying exact constitutive equation lacks a solution.
    """

    def __init__(self, disposition: SolverDisposition, message: str) -> None:
        if disposition not in (
            "domain_failure",
            "singular",
            "conditioning_failure",
            "nonfinite",
            "no_admitted_root",
            "multiple_admitted_roots",
        ):
            raise ValueError("expected a failed C stage disposition")
        super().__init__(message)
        self.disposition = disposition


def exact_matrix(matrix: Matrix) -> ExactMatrix:
    return tuple(tuple(Fraction(x) for x in row) for row in matrix)


def binary64_matrix(matrix: ExactMatrix) -> Matrix:
    try:
        return tuple(tuple(_computed(float(x)) for x in row) for row in matrix)
    except OverflowError as exc:
        raise MatrixError("nonfinite", "C stage result is not finite binary64") from exc


def transpose(matrix: ExactMatrix) -> ExactMatrix:
    return tuple(zip(*matrix, strict=True))


def matmul(left: ExactMatrix, right: ExactMatrix) -> ExactMatrix:
    return tuple(
        tuple(
            sum((a * b for a, b in zip(row, col, strict=True)), Fraction())
            for col in transpose(right)
        )
        for row in left
    )


def product(left: Matrix, right: Matrix) -> Matrix:
    return binary64_matrix(matmul(exact_matrix(left), exact_matrix(right)))


def identity(size: int) -> Matrix:
    return tuple(tuple(float(i == j) for j in range(size)) for i in range(size))


def apply(matrix: Matrix, values: tuple[float, ...]) -> tuple[float, ...]:
    result = binary64_matrix(
        matmul(exact_matrix(matrix), tuple((Fraction(x),) for x in values))
    )
    return tuple(row[0] for row in result)


def inverse(matrix: ExactMatrix) -> ExactMatrix:
    """Exact elimination of the supplied coefficients; never a pseudoinverse."""
    n = len(matrix)
    rows = [
        list(row) + [Fraction(i == j) for j in range(n)] for i, row in enumerate(matrix)
    ]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            raise MatrixError("singular", "singular C stage block; no fallback")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [x / divisor for x in rows[j]]
        for i in range(n):
            if i != j:
                factor = rows[i][j]
                rows[i] = [
                    a - factor * b for a, b in zip(rows[i], rows[j], strict=True)
                ]
    return tuple(tuple(row[n:]) for row in rows)


def inertia(matrix: ExactMatrix) -> tuple[int, int, int]:
    """Exact symmetric congruences, including a 2x2 pivot when diagonals vanish.

    Returns negative, zero, positive counts. No eigensolver tolerance decides
    whether the declared cutoff is exactly on the supplied mathematical spectrum.
    """
    rows = [list(row) for row in matrix]
    negative = positive = 0
    while rows:
        n = len(rows)
        pivot = next((i for i in range(n) if rows[i][i]), None)
        if pivot is not None:
            order = [pivot] + [i for i in range(n) if i != pivot]
            rows = [[rows[i][j] for j in order] for i in order]
            d = rows[0][0]
            negative += int(d < 0)
            positive += int(d > 0)
            rows = [
                [rows[i][j] - rows[i][0] * rows[0][j] / d for j in range(1, n)]
                for i in range(1, n)
            ]
        else:
            pair = next(
                ((i, j) for i in range(n) for j in range(i + 1, n) if rows[i][j]), None
            )
            if pair is None:
                return negative, n, positive
            i, j = pair
            order = [i, j] + [k for k in range(n) if k not in pair]
            rows = [[rows[i][j] for j in order] for i in order]
            b = rows[0][1]
            rows = [
                [
                    rows[i][j] - (rows[i][0] * rows[1][j] + rows[i][1] * rows[0][j]) / b
                    for j in range(2, n)
                ]
                for i in range(2, n)
            ]
            negative += 1
            positive += 1
    return negative, 0, positive



def _positive_semidefinite(matrix: ExactMatrix) -> bool:
    """Exact Schur-complement PSD decision for a symmetric Gram bound.

    A negative diagonal is incompatible with PSD. A positive diagonal permits
    an exact congruence reduction; if no positive diagonal remains, all entries
    must be zero. This also admits equality at a certified endpoint. Only the
    conditioning certificate uses this boolean decision; general inertia keeps
    its signed-rank contract.
    """
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
        reduced = [[Fraction()] * size for _ in range(size)]
        for i in range(size):
            gain = rows[i + 1][0] / diagonal
            for j in range(i, size):
                value = rows[i + 1][j + 1] - gain * rows[j + 1][0]
                reduced[i][j] = reduced[j][i] = value
        rows = reduced
    return True


def condition_bound(exact: ExactMatrix, limit: float, label: str) -> Fraction:
    """The exact conditioning algorithm; failure always uses the current label."""
    scale = max(abs(x) for row in exact for x in row)
    if not scale:
        raise MatrixError("singular", "singular " + label)
    normalized = tuple(tuple(x / scale for x in row) for row in exact)
    gram = matmul(transpose(normalized), normalized)
    n = len(gram)
    if not any(gram[i][j] for i in range(n) for j in range(n) if i != j):
        lower, upper = (
            min(gram[i][i] for i in range(n)),
            max(gram[i][i] for i in range(n)),
        )
        if lower <= 0:
            raise MatrixError("singular", "singular " + label)
    elif n == 2:
        # Squaring the exact 2x2 Gram eigenvalue ratio inequality avoids
        # deciding an equality from rounded singular-value endpoints.
        a, b, d = gram[0][0], gram[0][1], gram[1][1]
        if a * d <= b * b:
            raise MatrixError("singular", "singular " + label)
        trace, discriminant = a + d, (a - d) ** 2 + 4 * b * b
        k2 = Fraction(limit) ** 2
        if k2 < 1 or (k2 - 1) ** 2 * trace**2 < (k2 + 1) ** 2 * discriminant:
            raise MatrixError(
                "conditioning_failure", "conditioning limit exceeded: " + label
            )
        numerator = math.isqrt(discriminant.numerator)
        denominator = math.isqrt(discriminant.denominator)
        if (
            numerator**2 == discriminant.numerator
            and denominator**2 == discriminant.denominator
        ):
            root = Fraction(numerator, denominator)
            lower, upper = trace - root, trace + root
        else:
            lower, upper = Fraction(1), k2
    else:
        np = _dependency("numpy")
        try:
            singular = np.linalg.svd(
                np.array(binary64_matrix(normalized)), compute_uv=False
            )
        except np.linalg.LinAlgError as exc:
            raise MatrixError(
                "conditioning_failure", "conditioning decomposition failed: " + label
            ) from exc
        if not np.all(np.isfinite(singular)):
            raise MatrixError(
                "nonfinite", "nonfinite conditioning decomposition: " + label
            )
        if min(singular) <= 0:
            raise MatrixError(
                "conditioning_failure", "conditioning cannot resolve " + label
            )
        small, large = float(min(singular)), float(max(singular))
        for attempt in range(32):
            if attempt:
                error = math.ldexp(large, attempt - 52)
                small_bound, large_bound = small - error, large + error
            else:
                small_bound, large_bound = small, large
            if small_bound <= 0 or not math.isfinite(large_bound):
                raise MatrixError(
                    "conditioning_failure", "conditioning cannot resolve " + label
                )
            lower, upper = Fraction(small_bound) ** 2, Fraction(large_bound) ** 2
            low_test = tuple(
                tuple(x - (lower if i == j else 0) for j, x in enumerate(row))
                for i, row in enumerate(gram)
            )
            high_test = tuple(
                tuple((upper if i == j else 0) - x for j, x in enumerate(row))
                for i, row in enumerate(gram)
            )
            if _positive_semidefinite(low_test) and _positive_semidefinite(high_test):
                break
        else:
            raise MatrixError(
                "conditioning_failure", "conditioning certificate unresolved: " + label
            )
    bound = upper / lower
    if bound > Fraction(limit) ** 2:
        raise MatrixError(
            "conditioning_failure", "conditioning limit exceeded: " + label
        )
    return bound
