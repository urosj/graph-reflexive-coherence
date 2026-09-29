"""Shared V4 matrix API with automatic operation-owned fact reuse.

Realizations use this module, never the private arithmetic implementation.
Reuse applies only to successful exact inverse/conditioning facts. Every RHS,
residual and stage certificate remains fresh. Independent unscoped calls have
no shared lifetime. Use matrix_operation for scoped standalone calculations or
an explicit FRESH policy; nested scientific operations inherit that policy.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from fractions import Fraction

from . import _grc_v4_matrix as _backend
from ._grc_v4_matrix import (
    ExactMatrix,
    MatrixError,
    apply,
    binary64_matrix,
    exact_matrix,
    identity,
    inertia,
    matmul,
    product,
    transpose,
)
from .grc_v4_codec import _OPERATION_CONTEXT, _operation_contract_assets
from .grc_v4_geometry import Matrix
from .grc_v4_linear import MatrixReuse, _ConditionFact, _InverseFact
from .grc_v4_profile import SolverPolicy
from .grc_v4_state import FrozenJSONMap

__all__ = [
    "ExactMatrix",
    "MatrixError",
    "MatrixReuse",
    "apply",
    "binary64_matrix",
    "condition",
    "condition_bound",
    "exact_matrix",
    "identity",
    "inertia",
    "inverse",
    "matmul",
    "matrix_operation",
    "product",
    "residual_pass",
    "solve",
    "solve_positive",
    "transpose",
]


@contextmanager
def matrix_operation(*, reuse: MatrixReuse | None = None) -> Iterator[None]:
    """Choose one fact-reuse policy for a numerical/scientific operation scope.

    FRESH recalculates matrix facts; it does not relax solver or admission rules.
    Each nested public scientific operation still owns an independent store.
    """
    with _operation_contract_assets(matrix_reuse=reuse):
        yield


def inverse(matrix: ExactMatrix) -> ExactMatrix:
    """Exact inverse reuse by immutable coefficients within the current operation."""
    context = _OPERATION_CONTEXT.get()
    facts = None if context is None else context.matrix_facts
    if facts is not None:
        fact = facts.find(matrix)
        if fact is not None:
            return fact.inverse
    inverse = _backend.inverse(matrix)
    if facts is not None:
        facts.remember(_InverseFact(matrix, inverse))
    return inverse


def condition(matrix: Matrix, limit: float, label: str) -> FrozenJSONMap:
    """Certify a Euclidean 2-norm condition bound on these coordinates.

    SVD proposes endpoints only. Exact PSD tests on the normalized Gram matrix
    certify the endpoints, including equality. Unresolved bounds fail closed.
    """
    exact = exact_matrix(matrix)
    return _condition_certificate(condition_bound(exact, limit, label), limit, label)


def condition_bound(exact: ExactMatrix, limit: float, label: str) -> Fraction:
    """Reuse a successful proof for exactly these coefficients and this limit."""
    context = _OPERATION_CONTEXT.get()
    facts = None if context is None else context.matrix_facts
    exact_limit = Fraction(limit)
    if facts is not None:
        fact = facts.find(exact, exact_limit)
        if fact is not None:
            return fact.condition_upper_squared
    bound = _backend.condition_bound(exact, limit, label)
    if facts is not None:
        facts.remember(_ConditionFact(exact, exact_limit, bound))
    return bound


def _condition_certificate(bound: Fraction, limit: float, label: str) -> FrozenJSONMap:
    return FrozenJSONMap(
        {
            "block": label,
            "norm": "euclidean_2",
            "condition_upper_squared": str(bound),
            "limit": limit,
        }
    )


def residual_pass(
    residual: tuple[Fraction, ...], rhs: tuple[Fraction, ...], policy: SolverPolicy
) -> bool:
    """||r||2 <= atol + rtol max(1,||rhs||2), compared without underflow."""
    r2 = sum((x * x for x in residual), Fraction())
    b2 = max(Fraction(1), sum((x * x for x in rhs), Fraction()))
    a, b = Fraction(policy.absolute_tolerance), Fraction(policy.relative_tolerance)
    excess = r2 - a * a - b * b * b2
    return excess <= 0 or excess * excess <= 4 * a * a * b * b * b2


def solve(
    matrix: Matrix,
    rhs: Matrix,
    policy: SolverPolicy,
    label: str,
    certificates: list[FrozenJSONMap],
) -> Matrix:
    exact = exact_matrix(matrix)
    prepared_inverse = inverse(exact)
    certificates.append(
        _condition_certificate(
            condition_bound(exact, policy.conditioning_limit, label),
            policy.conditioning_limit,
            label,
        )
    )
    exact_rhs = exact_matrix(rhs)
    result = binary64_matrix(matmul(prepared_inverse, exact_rhs))
    observed = matmul(exact, exact_matrix(result))
    for residual, target in zip(
        transpose(
            tuple(
                tuple(a - b for a, b in zip(left, right, strict=True))
                for left, right in zip(observed, exact_rhs, strict=True)
            )
        ),
        transpose(exact_rhs),
        strict=True,
    ):
        if not residual_pass(residual, target, policy):
            raise MatrixError(
                "no_admitted_root", "declared residual tolerance failed: " + label
            )
    return result


def solve_positive(
    matrix: ExactMatrix, rhs: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    """Exact SPD normal-equation solve, with fresh domain and RHS checks.

    This is not a physical binary64 solver policy: callers own their declared
    output rounding. The successful inverse uses the same automatic fact store.
    """
    n = len(matrix)
    if len(rhs) != n or any(len(row) != n for row in matrix):
        raise ValueError("positive solve requires matching square coordinates")
    if any(matrix[i][j] != matrix[j][i] for i in range(n) for j in range(i)):
        raise ValueError("positive solve requires symmetric coefficients")
    if inertia(matrix) != (0, 0, n):
        raise MatrixError("domain_failure", "normal equations are not positive")
    exact_rhs = tuple((x,) for x in rhs)
    result = matmul(inverse(matrix), exact_rhs)
    if matmul(matrix, result) != exact_rhs:
        raise MatrixError("no_admitted_root", "exact positive solve residual failed")
    return tuple(row[0] for row in result)
