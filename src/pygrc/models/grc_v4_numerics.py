"""Shared V4 matrix API with automatic operation-owned fact reuse.

Realizations use this module, never the private arithmetic implementation.
Reuse applies to successful exact inverse/conditioning facts and certified
rounded solutions keyed by exact coefficients AND RHS. Every admission,
residual and stage certificate remains fresh. Independent unscoped calls have
no shared lifetime. Use matrix_operation for scoped standalone calculations or
an explicit FRESH policy; nested scientific operations inherit that policy.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

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
from .grc_v4_exact import ExactBackend, ExactScalar, exact_backend, exact_number
from .grc_v4_geometry import Matrix
from .grc_v4_linear import MatrixReuse, _ConditionFact, _InverseFact, _RoundedSolveFact
from .grc_v4_profile import SolverPolicy
from .grc_v4_state import FrozenJSONMap
from . import grc_v4_certification as _certified
from .grc_v4_certification import (
    CertificationInconclusive, NumericalPolicy, current_numerical_policy,
    numerical_policy,
)

__all__ = [
    "CertificationInconclusive",
    "NumericalPolicy",
    "current_numerical_policy",
    "numerical_policy",
    "ExactBackend",
    "ExactMatrix",
    "MatrixError",
    "MatrixReuse",
    "apply",
    "binary64_matrix",
    "condition",
    "condition_bound",
    "exact_backend",
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


def condition_bound(exact: ExactMatrix, limit: float, label: str) -> ExactScalar:
    """Reuse a successful proof for exactly these coefficients and this limit."""
    context = _OPERATION_CONTEXT.get()
    facts = None if context is None else context.matrix_facts
    exact_limit = exact_number(limit)
    if facts is not None:
        fact = facts.find(exact, exact_limit)
        if fact is not None:
            return fact.condition_upper_squared
    bound = (_certified.condition_bound(exact, limit) if _certified.certified_policy()
             else _backend.condition_bound(exact, limit, label))
    if facts is not None:
        facts.remember(_ConditionFact(exact, exact_limit, bound))
    return bound


def _condition_certificate(bound: ExactScalar, limit: float, label: str) -> FrozenJSONMap:
    return FrozenJSONMap(
        {
            "block": label,
            "norm": "euclidean_2",
            "condition_upper_squared": str(bound),
            "limit": limit,
        }
    )


def residual_pass(
    residual: tuple[ExactScalar, ...], rhs: tuple[ExactScalar, ...], policy: SolverPolicy
) -> bool:
    """||r||2 <= atol + rtol max(1,||rhs||2), compared without underflow."""
    r2 = sum((x * x for x in residual), exact_number())
    b2 = max(exact_number(1), sum((x * x for x in rhs), exact_number()))
    a, b = exact_number(policy.absolute_tolerance), exact_number(policy.relative_tolerance)
    excess = r2 - a * a - b * b * b2
    return excess <= 0 or excess * excess <= 4 * a * a * b * b * b2


def solve(
    matrix: Matrix,
    rhs: Matrix,
    policy: SolverPolicy,
    label: str,
    certificates: list[FrozenJSONMap],
    *,
    condition_witness: tuple | None = None,
) -> Matrix:
    exact = exact_matrix(matrix)
    use_certified = _certified.certified_policy()
    prepared_inverse = None if use_certified else inverse(exact)
    certificates.append(
        _condition_certificate(
            (_certified.condition_bound(exact, policy.conditioning_limit, gram_witness=condition_witness)
             if use_certified and condition_witness is not None else
             condition_bound(exact, policy.conditioning_limit, label)),
            policy.conditioning_limit,
            label,
        )
    )
    exact_rhs = exact_matrix(rhs)
    solve_fact = None
    facts = None
    if use_certified:
        context = _OPERATION_CONTEXT.get()
        facts = None if context is None else context.matrix_facts
        solve_fact = None if facts is None else facts.find_solve(exact, exact_rhs)
        result = (_certified.rounded_solve(exact, exact_rhs) if solve_fact is None
                  else solve_fact.result)
        certificates.append(FrozenJSONMap({"block": label, "execution_policy": current_numerical_policy().value,
                                          "rounding": "unique_binary64_nearest_even", "arb_precision_bits": 256}))
    else:
        assert prepared_inverse is not None
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
    if use_certified and facts is not None and solve_fact is None:
        facts.remember_solve(_RoundedSolveFact(exact, exact_rhs, result))
    return result


def solve_positive(
    matrix: ExactMatrix, rhs: tuple[ExactScalar, ...]
) -> tuple[ExactScalar, ...]:
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
