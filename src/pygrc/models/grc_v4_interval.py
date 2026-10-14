"""Fixed-precision interval matrix kernels for the explicit certified policy.

These enclose analytic equations; they never return a rounded physical current
or an exact inverse. No approximate solve, precision retry or legacy fallback.
"""
from .grc_v4_certification import (
    _ARB_CONTEXT_LOCK, certified_policy, CertificationInconclusive,
)
from .grc_v4_exact import ExactBackend, current_exact_backend, _flint_module, exact_number


def _require_policy():
    if not certified_policy() or current_exact_backend() is not ExactBackend.FLINT:
        raise ValueError("interval matrix kernels require explicit certified FLINT policy")


def _matrix(rows):
    flint = _flint_module()
    if rows and any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("ragged interval matrix")
    values = []
    for row in rows:
        out = []
        for lower, upper in row:
            lower, upper = exact_number(lower), exact_number(upper)
            if lower > upper:
                raise ValueError("reversed interval")
            # Even non-dyadic endpoints are outward-enclosed, not rounded into
            # point coefficients. Arb union includes both closed endpoints.
            out.append(flint.arb(lower).union(flint.arb(upper)))
        values.append(out)
    return flint.arb_mat(values)


def _endpoints(matrix):
    if any(not matrix[i, j].is_finite()
           for i in range(matrix.nrows()) for j in range(matrix.ncols())):
        raise CertificationInconclusive("nonfinite analytic interval matrix enclosure")
    return tuple(tuple((matrix[i,j].lower().fmpq(), matrix[i,j].upper().fmpq())
                       for j in range(matrix.ncols())) for i in range(matrix.nrows()))


def matmul(left, right):
    """Enclose every AB for A and B in the supplied entrywise boxes."""
    _require_policy()
    if not left:
        return ()
    if any(len(row) != len(right) for row in left):
        raise ValueError("interval product dimension mismatch")
    if not right:
        return tuple(() for _ in left)
    flint = _flint_module()
    with _ARB_CONTEXT_LOCK, flint.ctx.workprec(256):
        return _endpoints(_matrix(left) * _matrix(right))


def inverse(matrix):
    """Rigorous Arb inverse enclosure at 256 bits, or explicit inconclusive."""
    _require_policy()
    if any(len(row) != len(matrix) for row in matrix):
        raise ValueError("square interval inverse required")
    if not matrix:
        return ()
    flint = _flint_module()
    with _ARB_CONTEXT_LOCK, flint.ctx.workprec(256):
        operand = _matrix(matrix)
        try:
            result = operand.inv()
        except (ZeroDivisionError, ValueError) as exc:
            raise CertificationInconclusive("analytic interval inverse unresolved at 256 bits") from exc
        return _endpoints(result)
