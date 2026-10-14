"""Explicit bounded numerical policy; no fallback or scientific-state authority.

All sufficient proofs fail as CertificationInconclusive, not as mathematical
rejection. Exact inverse callers remain exact. See specs/grc-v4-numerical-policy.md.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from enum import Enum
import math
import struct
from threading import RLock

from .grc_v4_exact import (
    ExactBackend,
    _flint_module,
    current_exact_backend,
    exact_number,
)


class NumericalPolicy(Enum):
    LEGACY_EXACT = "legacy_exact_v1"
    CERTIFIED_ARB_256 = "certified_arb_256_weighted_v1"


class CertificationInconclusive(RuntimeError):
    """Selected execution proof could not resolve; no rejection or retry implied."""


_POLICY = ContextVar("grcv4_numerical_policy", default=NumericalPolicy.LEGACY_EXACT)
_ARB_CONTEXT_LOCK = RLock()


def current_numerical_policy():
    return _POLICY.get()


def certified_policy():
    return current_numerical_policy() is NumericalPolicy.CERTIFIED_ARB_256


@contextmanager
def numerical_policy(policy):
    if type(policy) is not NumericalPolicy:
        raise TypeError("expected a NumericalPolicy")
    if policy is NumericalPolicy.CERTIFIED_ARB_256:
        if current_exact_backend() is not ExactBackend.FLINT:
            raise ValueError(
                "certified numerical policy requires explicit FLINT backend"
            )
        _flint_module()
    token = _POLICY.set(policy)
    try:
        yield
    finally:
        _POLICY.reset(token)


def _matrix(rows):
    if current_exact_backend() is not ExactBackend.FLINT:
        raise ValueError("certified matrix kernels require the FLINT backend")
    return _flint_module().fmpq_mat([[exact_number(x) for x in row] for row in rows])


def _square(a):
    if a.nrows() != a.ncols():
        raise ValueError("square matrix required")


def _diagonal(a):
    return all(
        a[i, j] == 0 for i in range(a.nrows()) for j in range(a.ncols()) if i != j
    )


def _norms(a):
    q = exact_number
    one = max(
        (sum((abs(a[i, j]) for i in range(a.nrows())), q(0)) for j in range(a.ncols())),
        default=q(0),
    )
    infinity = max(
        (sum((abs(a[i, j]) for j in range(a.ncols())), q(0)) for i in range(a.nrows())),
        default=q(0),
    )
    return one, infinity


def round_interval(lo, hi):
    """Whole exact interval containment in one binary64 nearest/even cell."""
    q = exact_number
    lo, hi = q(lo), q(hi)
    if lo > hi:
        raise ValueError("inverted rounding interval")
    try:
        left, right = float(lo), float(hi)
    except OverflowError as exc:
        raise CertificationInconclusive(
            "binary64 overflow boundary unresolved"
        ) from exc
    if not math.isfinite(left) or not math.isfinite(right) or left != right:
        raise CertificationInconclusive("unique finite binary64 rounding unavailable")
    value = 0.0 if left == 0 else left
    if value == 0:
        low, high, even = -(q(2) ** -1075), q(2) ** -1075, True
    else:
        prev, nex = math.nextafter(value, -math.inf), math.nextafter(value, math.inf)
        low = ((q(prev) if math.isfinite(prev) else -(q(2) ** 1024)) + q(value)) / 2
        high = ((q(nex) if math.isfinite(nex) else q(2) ** 1024) + q(value)) / 2
        even = not (struct.unpack(">Q", struct.pack(">d", value))[0] & 1)
    if not (low <= lo <= hi <= high and (even or (lo > low and hi < high))):
        raise CertificationInconclusive("exact rounding-cell containment failed")
    return value


def rounded_solve(matrix, rhs):
    """Fixed structural route: exact diagonal, otherwise one 256-bit Arb LU."""
    f = _flint_module()
    a, b = _matrix(matrix), _matrix(rhs)
    _square(a)
    if b.nrows() != a.nrows():
        raise ValueError("RHS dimension mismatch")
    if not a.nrows():
        return ()
    if _diagonal(a):
        if any(a[i, i] == 0 for i in range(a.nrows())):
            raise CertificationInconclusive("diagonal solve has a zero pivot")
        return tuple(
            tuple(
                round_interval(b[i, j] / a[i, i], b[i, j] / a[i, i])
                for j in range(b.ncols())
            )
            for i in range(a.nrows())
        )
    with _ARB_CONTEXT_LOCK, f.ctx.workprec(256):
        aa, bb = f.arb_mat(a), f.arb_mat(b)
        for exact, balls in ((a, aa), (b, bb)):
            if not all(
                balls[i, j].is_exact() and balls[i, j].fmpq() == exact[i, j]
                for i in range(exact.nrows())
                for j in range(exact.ncols())
            ):
                raise CertificationInconclusive(
                    "256-bit exact input representation unavailable"
                )
        try:
            answer = aa.solve(bb, algorithm="lu")
        except ZeroDivisionError as exc:
            raise CertificationInconclusive(
                "fixed Arb LU could not certify the system"
            ) from exc
        rows = []
        for i in range(answer.nrows()):
            row = []
            for j in range(answer.ncols()):
                ball = answer[i, j]
                if not ball.is_finite():
                    raise CertificationInconclusive("nonfinite Arb enclosure")
                row.append(round_interval(ball.lower().fmpq(), ball.upper().fmpq()))
            rows.append(tuple(row))
        return tuple(rows)


def condition_bound(matrix, limit, *, gram_witness=None):
    """Exact sufficient 2-norm condition bound; witness choice precedes proof."""
    q, f = exact_number, _flint_module()
    a, limit = _matrix(matrix), q(limit)
    _square(a)
    if limit < 1:
        raise ValueError("conditioning limit must be at least one")
    n = a.nrows()
    if not n:
        return q(1)
    if gram_witness is not None:
        # Arbitrary incidence and positive diagonal vertex pairing. The scalar
        # center is a declared rule, not an assumption that retained H is scalar.
        incidence, vertex, retained, tau = gram_witness
        b, v, h, tau = _matrix(incidence), _matrix(vertex), _matrix(retained), q(tau)
        if (
            b.ncols() != n
            or v.nrows() != v.ncols()
            or v.nrows() != b.nrows()
            or h.nrows() != h.ncols()
            or h.nrows() != n
            or tau < 0
            or not _diagonal(v)
            or any(v[i, i] <= 0 for i in range(v.nrows()))
        ):
            raise ValueError("invalid Gram resolvent witness")
        scale = max(h[i, i] for i in range(n))
        if scale <= 0:
            raise CertificationInconclusive(
                "positive resolvent comparison scale unavailable"
            )
        weighted = f.fmpq_mat(
            [[b[i, j] / v[i, i] for j in range(n)] for i in range(b.nrows())]
        )
        eye = f.fmpq_mat([[int(i == j) for j in range(n)] for i in range(n)])
        center = eye + tau * scale * b.transpose() * weighted
        error = max(_norms(a - center))
        one, infinity = _norms(b)
        lower, upper = (
            1 - error,
            1
            + tau * scale * one * infinity / min(v[i, i] for i in range(v.nrows()))
            + error,
        )
    elif _diagonal(a):
        entries = [abs(a[i, i]) for i in range(n)]
        lower, upper = min(entries), max(entries)
    else:
        scale = a[0, 0]  # Fixed leading-diagonal center; no search/retry.
        if scale == 0:
            raise CertificationInconclusive(
                "nonzero leading-diagonal comparison scale unavailable"
            )
        eye = f.fmpq_mat([[int(i == j) for j in range(n)] for i in range(n)])
        deviation = max(_norms(a / scale - eye))
        lower, upper = abs(scale) * (1 - deviation), abs(scale) * (1 + deviation)
    if lower <= 0 or upper > limit * lower:
        raise CertificationInconclusive(
            "selected sufficient conditioning bound unresolved"
        )
    return (upper / lower) ** 2


def positive_definite(matrix):
    """Symmetric strict diagonal dominance with positive diagonal proves SPD."""
    a = _matrix(matrix)
    _square(a)
    if a != a.transpose():
        raise ValueError("exact symmetric Hodge required")
    for i in range(a.nrows()):
        if a[i, i] <= sum(
            (abs(a[i, j]) for j in range(a.ncols()) if j != i), exact_number(0)
        ):
            raise CertificationInconclusive(
                "strict positive Hodge row margin unavailable"
            )


def c_regularity(beta, tau, retained, vertex):
    """(1-beta)I + tau B^T H0^-1 B H is nonsingular by SPD similarity."""
    if exact_number(beta) >= 1 or exact_number(tau) < 0:
        raise CertificationInconclusive(
            "positive-similarity C regularity domain unavailable"
        )
    positive_definite(retained)
    v = _matrix(vertex)
    _square(v)
    if not _diagonal(v) or any(v[i, i] <= 0 for i in range(v.nrows())):
        raise CertificationInconclusive(
            "positive diagonal vertex reference unavailable"
        )


def weighted_split(residual, reference, tolerance):
    """Exact sufficient normalized OS norm bound; never computes inertia."""
    r, d, t = _matrix(residual), _matrix(reference), exact_number(tolerance)
    _square(r)
    n = r.nrows()
    if (
        d.nrows() != n
        or d.ncols() != n
        or r != r.transpose()
        or not _diagonal(d)
        or any(d[i, i] <= 0 for i in range(n))
        or t < 0
    ):
        raise ValueError(
            "symmetric residual, positive diagonal reference and nonnegative tolerance required"
        )
    bound = max(
        (
            sum((abs(r[i, j]) for j in range(n)), exact_number(0)) / d[i, i]
            for i in range(n)
        ),
        default=exact_number(0),
    )
    if bound > t:
        raise CertificationInconclusive(
            "weighted OS split bound inconclusive; no inertia fallback"
        )
    return {
        "method": "exact_weighted_row_sum_v1",
        "weighted_row_bound": str(bound),
        "tolerance_exact": str(t),
        "margin_lower": str(t - bound),
    }
