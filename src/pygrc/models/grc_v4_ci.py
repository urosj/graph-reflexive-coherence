"""Certified local A/C CI and CI+PC roots; no lifecycle or support authority.

The declared closed Frobenius ball is centred on the reference Hodge. Bounds
are derived from the supplied scientific inputs, never supplied as assertions
by the caller. C admits one whole-ball strict-gap stratum. A broader stratum
union, a disconnected branch, and an uncertified domain are unsupported.
The same bounds hold for every geometry gain between zero and the declared
gain, proving reference-branch connection. Numerical residuals are evaluated
independently of the contraction admission; convergence alone grants nothing.
CI+PC reads fixed old Z in the same root and retains its selected source for
one subsequent carrier write. Its uniform domain must cover the B_2R image.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from functools import lru_cache
from typing import TYPE_CHECKING, Any, TypeAlias, cast

from . import grc_v4_numerics as numerics
from .grc_v4_candidate_a import (
    ADMITTED_HISTORY_POLICIES,
    CandidateACurrent,
    CandidateADifferentialReference,
    CandidateAStageError,
    CandidateAWriter,
)
from .grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError, _c_components
from .grc_v4_exact import ExactScalar, exact_number, is_exact
from .grc_v4_geometry import (
    GeometryDomainError,
    GeometryStageInputs,
    GRCV4Geometry,
    H_profile,
    K4Tensor,
    NonfiniteGeometryError,
    OneForm,
    PhysicalFlux,
    StarAssembly,
    VertexScalar,
    _computed,
    _identity,
    _local_payload,
)
from .grc_v4_profile import CandidateAParams, CIPCParams, CISolverParams
from .grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState, _number

if TYPE_CHECKING:
    from .grc_v4_step import OperationStage, ProvisionalResourceStep

DOMAIN_PREFIX = "ci_reference_frobenius_ball_v1:"
SOLVER_ID = "ci_reduced_fixed_point_v1"
JOINT_NORM = "joint_current_geometry_l2_v1"
NUMERICS = "ci_analytic_residual_enclosure_binary64_v2"
CIPC_NUMERICS = "cipc_same_root_source_enclosed_zoh_binary64_v1"
Point: TypeAlias = CandidateACurrent | CandidateCCurrent


class CIStageError(ValueError):
    """A failed provisional CI stage; the lifecycle owner owns any receipt."""

    def __init__(self, disposition: str, message: str) -> None:
        super().__init__(message)
        self.disposition = disposition


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CIStageError("domain_failure", message)


def _sqrt_upper(q: ExactScalar) -> ExactScalar:
    """Rational upper bound with at least 80 significant binary digits."""
    if q == 0:
        return exact_number()
    if q < 0:
        raise ValueError("negative norm square")
    shift = max(0, 80 - (q.numerator.bit_length() - q.denominator.bit_length()) // 2)
    numerator = q.numerator << (2 * shift)
    root = math.isqrt(numerator // q.denominator)
    if root * root * q.denominator < numerator:
        root += 1
    return exact_number(root, 1 << shift)


def _norm(values: Any) -> ExactScalar:
    return _sqrt_upper(sum((exact_number(x) ** 2 for x in values), exact_number()))


def _opnorm(matrix: Any) -> ExactScalar:
    """sqrt(||A||_1 ||A||_inf), bounding the physical Euclidean operator."""
    if not matrix or not matrix[0]:
        return exact_number()
    rows = max(sum((abs(exact_number(x)) for x in row), exact_number()) for row in matrix)
    columns = max(
        sum((abs(exact_number(x)) for x in col), exact_number())
        for col in zip(*matrix, strict=True)
    )
    return _sqrt_upper(rows * columns)


@lru_cache(maxsize=128, typed=True)
def _exp_bounds(q: ExactScalar) -> tuple[ExactScalar, ExactScalar]:
    """Exact outward enclosure: positive Taylor tail, dyadic range reduction.

    Only immutable scalar inputs and exact endpoints are memoized.
    Each squaring is rounded outward to a 160-bit absolute grid to bound work.
    Negative arguments use reciprocal interval endpoints. No platform exp,
    floating estimate, or mutable Decimal context decides an admission.
    """
    _require(abs(q) <= 1024, "exponential enclosure exceeds the declared finite budget")
    if q < 0:
        lo, hi = _exp_bounds(-q)
        return 1 / hi, 1 / lo
    scale, x = 0, q
    while x > exact_number(1, 2):
        scale, x = scale + 1, x / 2
    term = total = exact_number(1)
    for k in range(1, 33):
        term = term * x / k
        total += term
    tail = (term * x / 33) / (1 - x / 34)
    grid = 1 << 160

    def down(value: ExactScalar) -> ExactScalar:
        return exact_number(value.numerator * grid // value.denominator, grid)

    def up(value: ExactScalar) -> ExactScalar:
        return exact_number(-(-value.numerator * grid // value.denominator), grid)

    lo, hi = down(total), up(total + tail)
    for _ in range(scale):
        lo, hi = down(lo * lo), up(hi * hi)
    return lo, hi


@dataclass(frozen=True, slots=True)
class _Interval:
    """Rational enclosure. Point arithmetic stays exact; widths round outward.

    The 160 significant binary digit grid bounds denominator growth, including
    subnormal/large operands. No floating result or platform libm decides a
    residual bound. These are evaluation enclosures, not sampled derivatives.
    """

    lo: ExactScalar
    hi: ExactScalar

    def __post_init__(self) -> None:
        assert self.lo <= self.hi
        if self.lo == self.hi:
            return
        magnitude = max(abs(self.lo), abs(self.hi))
        shift = 160 - (
            magnitude.numerator.bit_length() - magnitude.denominator.bit_length()
        )
        grid = exact_number(2) ** shift
        for key, value in (("lo", self.lo), ("hi", -self.hi)):
            scaled = value * grid
            bound = exact_number(scaled.numerator // scaled.denominator) / grid
            object.__setattr__(self, key, bound if key == "lo" else -bound)

    def __add__(self, other: Any) -> _Interval:
        b = _iv(other)
        return _Interval(self.lo + b.lo, self.hi + b.hi)

    __radd__ = __add__

    def __neg__(self) -> _Interval:
        return _Interval(-self.hi, -self.lo)

    def __sub__(self, other: Any) -> _Interval:
        return self + -_iv(other)

    def __rsub__(self, other: Any) -> _Interval:
        return _iv(other) + -self

    def __mul__(self, other: Any) -> _Interval:
        b = _iv(other)
        ends = (self.lo * b.lo, self.lo * b.hi, self.hi * b.lo, self.hi * b.hi)
        return _Interval(min(ends), max(ends))

    __rmul__ = __mul__

    def __truediv__(self, other: Any) -> _Interval:
        b = _iv(other)
        if b.lo <= 0 <= b.hi:
            raise CIStageError(
                "no_admitted_root", "unresolved analytic evaluation divisor"
            )
        return self * _Interval(1 / b.hi, 1 / b.lo)

    @property
    def magnitude(self) -> ExactScalar:
        return max(abs(self.lo), abs(self.hi))


def _iv(x: Any) -> _Interval:
    return x if isinstance(x, _Interval) else _Interval(exact_number(x), exact_number(x))


def _iexp(x: _Interval) -> _Interval:
    return _Interval(_exp_bounds(x.lo)[0], _exp_bounds(x.hi)[1])


def _itanh(x: _Interval) -> _Interval:
    def endpoint(q: ExactScalar) -> _Interval:
        if q < 0:
            return -endpoint(-q)
        # Monotonic real saturation enclosure; no overflowing quotient or
        # assumption that a rounded tanh equals its real value.
        e = _Interval(*_exp_bounds(-2 * min(q, exact_number(512))))
        value = (_iv(1) - e) / (_iv(1) + e)
        return _Interval(value.lo, exact_number(1)) if q > 512 else value

    return _Interval(endpoint(x.lo).lo, endpoint(x.hi).hi)


def _im(matrix: Any) -> Any:
    return tuple(tuple(_iv(x) for x in row) for row in matrix)


def _imm(a: Any, b: Any) -> Any:
    return tuple(
        tuple(
            sum((x * y for x, y in zip(row, col, strict=True)), _iv(0))
            for col in zip(*b, strict=True)
        )
        for row in a
    )


def _iinverse(a: Any) -> Any:
    """Verified midpoint inverse: ||I-M A||_inf=q<1 bounds the Neumann tail."""
    mid = tuple(tuple((x.lo + x.hi) / 2 for x in row) for row in a)
    try:
        inverse = numerics.inverse(mid)
    except CandidateCStageError as exc:
        raise CIStageError(
            "no_admitted_root", "unresolved analytic matrix inverse"
        ) from exc
    residual = _imm(_im(inverse), a)
    q = max(
        sum(((int(i == j) - x).magnitude for j, x in enumerate(row)), exact_number())
        for i, row in enumerate(residual)
    )
    if q >= 1:
        raise CIStageError(
            "no_admitted_root", "analytic inverse enclosure is unresolved"
        )
    norm = max(sum(map(abs, row), exact_number()) for row in inverse)
    error = q * norm / (1 - q)
    return tuple(tuple(_Interval(x - error, x + error) for x in row) for row in inverse)


def _a_descriptors_exact(point: CandidateACurrent) -> Any:
    """Rebuild the declared differential linear systems before output rounding."""
    backend, c = point.differential_reference, point.inputs.current.C
    graph, d = backend.graph, backend.dimension
    result = []
    for i, node in enumerate(graph.live_node_ids):
        a = [
            [exact_number(backend.regularization) * int(k == j) for j in range(d)]
            for k in range(d)
        ]
        b = [[exact_number()] for _ in range(d)]
        for edge in graph.oriented_edges:
            if node not in (edge.tail_node_id, edge.head_node_id):
                continue
            other = (
                edge.head_node_id if node == edge.tail_node_id else edge.tail_node_id
            )
            j = graph.node_index(other)
            delta = [
                exact_number(y) - exact_number(x)
                for x, y in zip(backend.positions[i], backend.positions[j], strict=True)
            ]
            w = exact_number(cast(float, backend.reference_weights[edge.edge_id]))
            for k in range(d):
                b[k][0] += w * delta[k] * (exact_number(c[j]) - exact_number(c[i]))
                for column in range(d):
                    a[k][column] += w * delta[k] * delta[column]
        result.append(
            tuple(
                row[0]
                for row in numerics.matmul(numerics.inverse(tuple(map(tuple, a))), tuple(map(tuple, b)))
            )
        )
    return tuple(result)


def _projector_enclosure(point: CandidateCCurrent) -> Any:
    """Enclose the exact strict-cut spectral projector, independently of libm.

    Form an exact rational orthoprojector E onto a rank-r subspace suggested
    by the rounded projector (pivoted rational Gram-Schmidt). Verify the two
    compressed spectral signs by exact inertia. For S=E A E+(I-E) A (I-E),
    g=1/|| (S-Lambda I)^-1 || and e>=||A-S||_F, e<g prevents cutoff crossings.
    The separated-spectrum Sylvester bound gives ||P(A)-E||_F <=2e/(g-e).
    Thus numerical eigenvectors suggest a subspace but cannot certify it.
    """
    selector = point.algebra.selector
    graph = point.inputs.geometry.reference.graph
    n, rank = len(graph.live_node_ids), selector.rank
    eye = tuple(tuple(exact_number(i == j) for j in range(n)) for i in range(n))
    if rank in (0, n):
        return _im(eye if rank == n else tuple((exact_number(),) * n for _ in range(n)))
    components = _c_components(graph)
    if rank == len(components):
        projection = [[exact_number() for _ in range(n)] for _ in range(n)]
        for group in components:
            for i in group:
                for j in group:
                    projection[i][j] = exact_number(1, len(group))
        return _im(projection)
    columns = [
        list(map(exact_number, col)) for col in zip(*selector.projector, strict=True)
    ]
    projection = [[exact_number() for _ in range(n)] for _ in range(n)]
    for _ in range(rank):
        v = max(columns, key=lambda col: sum(x * x for x in col))
        square = sum((x * x for x in v), exact_number())
        if square == 0:
            raise CIStageError("no_admitted_root", "unresolved projector basis")
        for i in range(n):
            for j in range(n):
                projection[i][j] += v[i] * v[j] / square
        columns = [
            [
                x
                - sum((a * b for a, b in zip(col, v, strict=True)), exact_number())
                * y
                / square
                for x, y in zip(col, v, strict=True)
            ]
            for col in columns
        ]
    e = tuple(map(tuple, projection))
    complement = tuple(
        tuple(x - y for x, y in zip(row, other, strict=True))
        for row, other in zip(eye, e, strict=True)
    )
    b = numerics.exact_matrix(graph.incidence)
    a = numerics.matmul(
        numerics.matmul(b, numerics.exact_matrix(point.inputs.geometry.one_form_hodge.matrix)), numerics.transpose(b)
    )
    left, right = numerics.matmul(numerics.matmul(e, a), e), numerics.matmul(numerics.matmul(complement, a), complement)
    cutoff = exact_number(point.algebra.transport.params.Lambda_C)
    signs = (
        tuple(
            tuple(cutoff * e[i][j] - left[i][j] + complement[i][j] for j in range(n))
            for i in range(n)
        ),
        tuple(
            tuple(right[i][j] - cutoff * complement[i][j] + e[i][j] for j in range(n))
            for i in range(n)
        ),
    )
    if any(numerics.inertia(s) != (0, 0, n) for s in signs):
        raise CIStageError(
            "no_admitted_root", "projector spectral signs are unresolved"
        )
    shifted = tuple(
        tuple(left[i][j] + right[i][j] - cutoff * eye[i][j] for j in range(n))
        for i in range(n)
    )
    gap = 1 / _opnorm(numerics.inverse(shifted))
    error = _norm(
        a[i][j] - left[i][j] - right[i][j] for i in range(n) for j in range(n)
    )
    if error >= gap:
        raise CIStageError("no_admitted_root", "projector enclosure reaches cutoff")
    bound = 2 * error / (gap - error)
    return tuple(tuple(_Interval(x - bound, x + bound) for x in row) for row in e)


def _analytic_residual(point: Point, current: PhysicalFlux) -> tuple[Any, Any]:
    """Evaluate the same real equations as the domain proof at represented J,h.

    All declared binary64 inputs are exact real operands. Mobility products,
    differential solves, nonlinear functions, selector, matrix inverses and
    overlap square roots are enclosed before any constitutive output rounding.
    """
    inputs, ref = point.inputs, point.inputs.geometry.reference
    graph, p = ref.graph, ref.profile.params_resolved.candidate
    h = numerics.exact_matrix(inputs.geometry.one_form_hodge.matrix)
    b = _im(graph.incidence)
    bt, ih = tuple(zip(*b, strict=True)), _im(numerics.inverse(h))
    c, j = (
        _im(tuple((x,) for x in inputs.current.C)),
        _im(tuple((x,) for x in current.values)),
    )
    gradient = _imm(bt, c)
    if isinstance(point, CandidateACurrent):
        assert isinstance(p, CandidateAParams)
        w = inputs.current.W_A
        assert w is not None
        href = numerics.exact_matrix(ref.pairings.one_form.matrix)
        potential_h = _im(
            tuple(
                tuple(
                    exact_number(p.kappa_c) * exact_number(w[i]) * int(i == k)
                    + exact_number(p.kappa_Ah) * (h[i][k] - href[i][k])
                    for k in range(len(h))
                )
                for i in range(len(h))
            )
        )
        raw = _imm(bt, _imm(b, _imm(potential_h, gradient)))
        baseline = tuple(
            (-exact_number(p.eta) * exact_number(wi) * row[0],)
            for wi, row in zip(w, raw, strict=True)
        )
        descriptors = _a_descriptors_exact(point)
        flux: Any = []
        for i, edge in enumerate(graph.oriented_edges):
            u, v = (
                graph.node_index(edge.tail_node_id),
                graph.node_index(edge.head_node_id),
            )
            square = sum(
                (
                    (x - y) ** 2
                    for x, y in zip(descriptors[u], descriptors[v], strict=True)
                ),
                exact_number(),
            )
            exponent = (
                -(
                    exact_number(p.alpha)
                    * (exact_number(inputs.current.C[u]) + exact_number(inputs.current.C[v]))
                    + exact_number(p.beta) * square
                    + exact_number(p.gamma) * baseline[i][0].lo ** 2
                )
                / 2
            )
            if exponent < -1000:
                target = _iv(p.W_floor)
            else:
                exp = _iexp(_iv(exponent))
                target = _Interval(
                    max(exact_number(p.W_floor), exp.lo), max(exact_number(p.W_floor), exp.hi)
                )
            contrast = (_iv(w[i]) - target) / (_iv(w[i]) + target)
            flux.append((exact_number(p.chi_A) * contrast * j[i][0],))
        flux = tuple(flux)
    else:
        p = point.algebra.transport.params
        if p.kappa_M_C == 0:
            retained = _im(h)
        else:
            selected = _imm(_projector_enclosure(point), c)
            rho = tuple(_itanh(row[0] / p.C_ref) for row in selected)
            deformation = tuple(
                _iexp(
                    exact_number(p.kappa_M_C)
                    / 4
                    * (
                        rho[graph.node_index(edge.tail_node_id)]
                        + rho[graph.node_index(edge.head_node_id)]
                    )
                )
                for edge in graph.oriented_edges
            )
            retained = tuple(
                tuple(deformation[i] * x * deformation[k] for k, x in enumerate(row))
                for i, row in enumerate(h)
            )
        raw = _imm(bt, _imm(b, _imm(retained, gradient)))
        baseline = tuple(
            (
                -exact_number(p.eta_C)
                * exact_number(cast(float, p.W_C_tr[e]))
                * exact_number(p.kappa_Phi_C)
                * row[0],
            )
            for e, row in zip(graph.live_edge_ids, raw, strict=True)
        )
        if p.tau_C == 0:
            flux = tuple((exact_number(p.chi_C) * row[0],) for row in j)
        else:
            lap = _imm(_imm(bt, b), retained)
            resolvent = _iinverse(
                tuple(
                    tuple(
                        int(i == k) + exact_number(p.tau_C) * x for k, x in enumerate(row)
                    )
                    for i, row in enumerate(lap)
                )
            )
            q = _imm(retained, _imm(ih, ih))
            qi = _imm(_im(numerics.matmul(h, h)), _iinverse(retained))
            flux = tuple(
                (exact_number(p.chi_C) * row[0],)
                for row in _imm(qi, _imm(resolvent, _imm(q, j)))
            )
    flat = _imm(ih, flux)
    fj = tuple(
        row[0] - base[0] - _gain(point) * read[0]
        for row, base, read in zip(j, baseline, flux, strict=True)
    )
    stars = tuple(set(graph.star(v)) for v in graph.live_node_ids)
    counts = [sum(i in star for star in stars) for i in range(len(h))]
    href = numerics.exact_matrix(ref.pairings.one_form.matrix)
    gain = exact_number(ref.profile.params_resolved.geometry.kappa_H) * _gain(point)
    old = _old_carrier(inputs)
    geometry_gain = exact_number(ref.profile.params_resolved.geometry.kappa_H)
    fh = []
    for i, row in enumerate(h):
        out = []
        for k, x in enumerate(row):
            count = sum(i in star and k in star for star in stars)
            radicand = exact_number(counts[i] * counts[k])
            upper = _sqrt_upper(radicand)
            coefficient = _iv(count) / _Interval(radicand / upper, upper)
            out.append(
                x
                - exact_number(href[i][k])
                - geometry_gain * old[i][k]
                - gain * coefficient * flat[i][0] * flat[k][0]
            )
        fh.append(tuple(out))
    return fj, tuple(fh)


@dataclass(frozen=True, slots=True)
class CIBoundedDomain:
    """Identity-bearing radius; the centre and norm are fixed by this recipe."""

    radius: float

    def __post_init__(self) -> None:
        radius = _number(self.radius)
        _require(radius > 0, "CI requires a positive bounded-domain radius")
        object.__setattr__(self, "radius", radius)

    @property
    def identity(self) -> str:
        return DOMAIN_PREFIX + self.radius.hex()

    @classmethod
    def from_identity(cls, name: str) -> CIBoundedDomain:
        _require(
            type(name) is str and name.startswith(DOMAIN_PREFIX),
            "unsupported CI domain declaration",
        )
        try:
            result = cls(float.fromhex(name[len(DOMAIN_PREFIX) :]))
        except (ValueError, OverflowError) as exc:
            raise CIStageError("domain_failure", "invalid CI domain radius") from exc
        _require(result.identity == name, "noncanonical CI domain identity")
        return result


def _declarations(inputs: GeometryStageInputs) -> CIBoundedDomain:
    if type(inputs) is not GeometryStageInputs:
        raise TypeError("CI requires typed captured inputs")
    profile = inputs.geometry.reference.profile
    identity, params = profile.identity_payload, profile.params_resolved
    realization, solver = params.realization, params.solver
    _require(
        (
            (
                identity.profile_family_id in {"A_CI", "C_CI"}
                and type(realization) is CISolverParams
            )
            or (
                identity.profile_family_id in {"A_CI_PC", "C_CI_PC"}
                and type(realization) is CIPCParams
                and realization.rho_inst == 1
            )
        )
        and identity.solver_id == SOLVER_ID
        and solver.solver_kind == "fixed_point"
        and realization.residual_norm_id == JOINT_NORM
        and solver.residual_norm_id == "edge_l2_v1"
        and realization.iteration_limit == solver.iteration_limit,
        "unimplemented or inconsistent CI solver declaration",
    )
    assert isinstance(realization, (CISolverParams, CIPCParams))
    return CIBoundedDomain.from_identity(realization.contraction_domain_id)


def _old_carrier(inputs: GeometryStageInputs) -> tuple[tuple[ExactScalar, ...], ...]:
    """Old Z is a fixed root input; CI has the exact zero offset."""
    n = len(inputs.geometry.reference.graph.live_edge_ids)
    z = inputs.current.Z_4
    return tuple(
        tuple(exact_number(0 if z is None else z[i * n + j]) for j in range(n))
        for i in range(n)
    )


def _effective_source(inputs: GeometryStageInputs, source: K4Tensor) -> K4Tensor:
    if inputs.current.Z_4 is None:
        return source
    old = _old_carrier(inputs)
    try:
        increment = tuple(
            tuple(_computed(float(z + exact_number(s))) for z, s in zip(a, b, strict=True))
            for a, b in zip(old, source.increment, strict=True)
        )
    except OverflowError as exc:
        raise CIStageError(
            "nonfinite", "CI+PC effective structural input exceeds binary64 range"
        ) from exc
    return K4Tensor(source.graph, source.base, increment)


def _point(
    inputs: GeometryStageInputs, backend: CandidateADifferentialReference | None
) -> Point:
    if inputs.geometry.reference.profile.identity_payload.candidate == "A":
        if type(backend) is not CandidateADifferentialReference:
            raise TypeError("A_CI requires its declared differential reference")
        return CandidateACurrent(inputs, backend)
    if backend is not None:
        raise TypeError("C_CI has no Candidate A differential input")
    return CandidateCCurrent(inputs)


def _gain(point: Point) -> ExactScalar:
    params = point.inputs.geometry.reference.profile.params_resolved.candidate
    return exact_number(
        params.zeta_A if isinstance(params, CandidateAParams) else params.zeta_C
    )


def _baseline(point: Point) -> PhysicalFlux:
    return (
        point.baseline
        if isinstance(point, CandidateACurrent)
        else point.algebra.baseline
    )


def _source(point: Point, current: PhysicalFlux) -> K4Tensor:
    return _source_from_flat(
        point, None if _gain(point) == 0 else point.read_back(current).causal_flat
    )


def _source_from_flat(point: Point, causal_flat: OneForm | None) -> K4Tensor:
    ref = point.inputs.geometry.reference
    gain = _gain(point)
    n = len(ref.graph.live_edge_ids)
    # chi is already in the read. zeta is outside the quadratic star adapter.
    if gain != 0 and causal_flat is None:
        raise TypeError("nonzero CI structural source requires its lowered read")
    try:
        increment = (
            tuple((0.0,) * n for _ in range(n))
            if gain == 0
            else tuple(
                tuple(_computed(float(gain * exact_number(x))) for x in row)
                for row in StarAssembly(cast(OneForm, causal_flat)).matrix
            )
        )
    except OverflowError as exc:
        raise CIStageError(
            "nonfinite", "CI structural source exceeds binary64 range"
        ) from exc
    return K4Tensor(ref.graph, ref.K4_base, increment)


@dataclass(frozen=True, slots=True)
class CITrial:
    """Fresh numerical trial plus an independent analytic residual enclosure."""

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference | None = None
    point: Point = field(init=False)
    generated: GRCV4Geometry = field(init=False)
    structural_source: K4Tensor = field(init=False)
    current_residual: tuple[ExactScalar, ...] = field(init=False)
    geometry_residual: tuple[tuple[ExactScalar, ...], ...] = field(init=False)
    analytic_current_residual: tuple[_Interval, ...] = field(init=False)
    analytic_geometry_residual: tuple[tuple[_Interval, ...], ...] = field(init=False)

    def __post_init__(self) -> None:
        domain = _declarations(self.inputs)
        _require(
            self.inputs.stage
            == ("cipc_trial" if self.inputs.current.Z_4 is not None else "ci_trial"),
            "CI residual requires its realization's joint trial stage",
        )
        _in_ball(self.inputs.geometry, domain)
        trial = self.inputs.trial_current
        assert trial is not None
        point = _point(self.inputs, self.differential_reference)
        # Consume only this fresh point's construction identity. Trial-current
        # flux, certified solve and residual evaluation still run independently.
        read = point._read_back(trial, point.read.source_identity)
        ref = self.inputs.geometry.reference
        source = _source_from_flat(point, read.causal_flat)
        generated = H_profile(
            _effective_source(self.inputs, source),
            reference=ref,
            context=ref.context,
            profile=ref.profile,
        )
        fj = tuple(
            exact_number(j) - exact_number(j0) - _gain(point) * exact_number(r)
            for j, j0, r in zip(
                trial.values, _baseline(point).values, read.flux.values, strict=True
            )
        )
        fh = tuple(
            tuple(
                exact_number(x)
                - exact_number(y)
                - exact_number(ref.profile.params_resolved.geometry.kappa_H)
                * (z + exact_number(s))
                for x, y, z, s in zip(a, b, old, c, strict=True)
            )
            for a, b, old, c in zip(
                self.inputs.geometry.one_form_hodge.matrix,
                ref.pairings.one_form.matrix,
                _old_carrier(self.inputs),
                source.increment,
                strict=True,
            )
        )
        analytic_j, analytic_h = _analytic_residual(point, trial)
        for name, value in (
            ("point", point),
            ("generated", generated),
            ("structural_source", source),
            ("current_residual", fj),
            ("geometry_residual", fh),
            ("analytic_current_residual", analytic_j),
            ("analytic_geometry_residual", analytic_h),
        ):
            object.__setattr__(self, name, value)

    @property
    def residual_squared(self) -> ExactScalar:
        """Certified upper bound for ||F(J,h)||^2 of the analytic equations."""
        return sum(
            (x.magnitude**2 for x in self.analytic_current_residual), exact_number()
        ) + sum(
            (x.magnitude**2 for row in self.analytic_geometry_residual for x in row),
            exact_number(),
        )


def _in_ball(geometry: GRCV4Geometry, domain: CIBoundedDomain) -> None:
    square = sum(
        (
            (exact_number(x) - exact_number(y)) ** 2
            for row, other in zip(
                geometry.one_form_hodge.matrix,
                geometry.reference.pairings.one_form.matrix,
                strict=True,
            )
            for x, y in zip(row, other, strict=True)
        ),
        exact_number(),
    )
    _require(
        square <= exact_number(domain.radius) ** 2,
        "CI geometry is outside its declared reference ball",
    )


def _a_read_bounds(
    point: CandidateACurrent, radius: ExactScalar, lower: ExactScalar
) -> dict[str, Any]:
    """Whole-ball A current/flat-read bounds, including the in-root G_W law."""
    ref = point.inputs.geometry.reference
    p = ref.profile.params_resolved.candidate
    assert isinstance(p, CandidateAParams)
    b = numerics.exact_matrix(ref.graph.incidence)
    gram = numerics.matmul(numerics.transpose(b), b)
    c = tuple(exact_number(x) for x in point.inputs.current.C)
    dc = tuple(
        sum((row[i] * c[i] for i in range(len(c))), exact_number())
        for row in numerics.transpose(b)
    )
    dc_norm = _norm(dc)
    weights = point.inputs.current.W_A
    assert weights is not None
    mobility = tuple(exact_number(p.eta) * exact_number(w) for w in weights)
    descriptors = _a_descriptors_exact(point)
    # Compute the unrounded analytic reference baseline independently of the
    # floating stage; only that smooth map is used for derivative bounds.
    jref = tuple(
        -exact_number(m)
        * exact_number(p.kappa_c)
        * sum(
            (
                g * exact_number(other) * d
                for g, other, d in zip(row, weights, dc, strict=True)
            ),
            exact_number(),
        )
        for m, row in zip(mobility, gram, strict=True)
    )
    lj = tuple(
        abs(exact_number(m) * exact_number(p.kappa_Ah)) * _norm(row) * dc_norm
        for m, row in zip(mobility, gram, strict=True)
    )
    qbounds, qlips, dlow, dhigh, jbounds, charts = [], [], [], [], [], []
    beta = exact_number(p.zeta_A) * exact_number(p.chi_A)
    for edge, w, j, lip in zip(
        ref.graph.oriented_edges, weights, jref, lj, strict=True
    ):
        u, v = (
            ref.graph.node_index(edge.tail_node_id),
            ref.graph.node_index(edge.head_node_id),
        )
        square = sum(
            (
                (exact_number(x) - exact_number(y)) ** 2
                for x, y in zip(descriptors[u], descriptors[v], strict=True)
            ),
            exact_number(),
        )
        constant = -(exact_number(p.alpha) * (c[u] + c[v]) + exact_number(p.beta) * square) / 2
        lo, hi = j - lip * radius, j + lip * radius
        smin = exact_number() if lo <= 0 <= hi else min(lo * lo, hi * hi)
        smax = max(lo * lo, hi * hi)
        exponents = (
            constant - exact_number(p.gamma) * smin / 2,
            constant - exact_number(p.gamma) * smax / 2,
        )
        emin, emax = min(exponents), max(exponents)
        floor = exact_number(p.W_floor)
        if emax < -1000:
            wl = wh = floor
            qlip, chart = exact_number(), "floor_active"
        else:
            _require(emax <= 1000, "A CI exponential range is not finite-certified")
            el = exact_number() if emin < -1000 else _exp_bounds(emin)[0]
            eh = _exp_bounds(emax)[1]
            _require(
                eh <= exact_number(float.fromhex("0x1.fffffffffffffp+1023")),
                "A CI exponential exceeds binary64 range",
            )
            if eh < floor:
                wl = wh = floor
                qlip, chart = exact_number(), "floor_active"
            else:
                _require(
                    el > floor or emin == emax,
                    "A CI domain crosses the conductance floor chart",
                )
                wl, wh = max(floor, el), max(floor, eh)
                qlip = abs(exact_number(p.gamma)) * max(abs(lo), abs(hi)) * lip / 2
                chart = "constant_exponent" if emin == emax else "floor_inactive"
        qlo, qhi = (
            (exact_number(w) - wh) / (exact_number(w) + wh),
            (exact_number(w) - wl) / (exact_number(w) + wl),
        )
        ends = (1 - beta * qlo, 1 - beta * qhi)
        _require(
            not min(ends) <= 0 <= max(ends),
            "A CI domain does not certify a regular current block",
        )
        dlow.append(min(map(abs, ends)))
        dhigh.append(max(map(abs, ends)))
        qbounds.append(max(abs(qlo), abs(qhi)))
        qlips.append(qlip)
        jbounds.append(max(abs(lo), abs(hi)))
        charts.append(chart)
    margin = min(dlow, default=exact_number(1))
    condition = max(dhigh, default=exact_number(1)) / margin
    _require(
        condition <= exact_number(ref.profile.params_resolved.solver.conditioning_limit),
        "A CI whole-domain current conditioning is uncertified",
    )
    j0, lj0 = _norm(jbounds), _norm(lj)
    qmax, lq = max(qbounds, default=exact_number()), max(qlips, default=exact_number())
    current = j0 / margin
    current_lip = lj0 / margin + j0 * abs(beta) * lq / margin**2
    chi = abs(exact_number(p.chi_A))
    flat = chi * qmax * current / lower
    flat_lip = chi * (
        qmax * current / lower**2 + (lq * current + qmax * current_lip) / lower
    )
    return dict(
        flat=flat,
        flat_lip=flat_lip,
        current=current,
        current_lip=current_lip,
        current_inverse=1 / margin,
        conditioning_upper=condition,
        floor_charts=charts,
    )


def _c_read_bounds(
    point: CandidateCCurrent, radius: ExactScalar, lower: ExactScalar, upper: ExactScalar
) -> dict[str, Any]:
    """Physical-coordinate bounds; retained positivity is not a flux margin."""
    ref, p = point.inputs.geometry.reference, point.algebra.transport.params
    b = numerics.exact_matrix(ref.graph.incidence)
    bt = numerics.transpose(b)
    b2 = _opnorm(numerics.matmul(bt, b))
    stiffness = numerics.matmul(numerics.matmul(b, numerics.exact_matrix(ref.pairings.one_form.matrix)), bt)
    shifted = tuple(
        tuple(x - (exact_number(p.Lambda_C) if i == j else 0) for j, x in enumerate(row))
        for i, row in enumerate(stiffness)
    )
    inverse = numerics.inverse(shifted)
    invnorm = _opnorm(inverse)
    gap = 1 / invnorm - b2 * radius
    _require(gap > 0, "C CI ball reaches an uncertified selector stratum boundary")
    # DP's Frobenius bound follows the symmetric separated-spectrum Sylvester
    # equation. 2/gap is conservative for the two off-diagonal projector blocks.
    sector_lip = 2 * b2 * _norm(point.inputs.current.C) / gap
    d = _exp_bounds(abs(exact_number(p.kappa_M_C)) / 2)[1]
    d_lip = d * abs(exact_number(p.kappa_M_C)) * sector_lip / (2 * exact_number(p.C_ref))
    retained_upper, retained_lower = d * d * upper, lower / (d * d)
    retained_lip = d * d + 2 * d * upper * d_lip
    dc = tuple(
        sum(
            (row[i] * exact_number(x) for i, x in enumerate(point.inputs.current.C)),
            exact_number(),
        )
        for row in bt
    )
    base_factor = (
        max(
            (
                exact_number(p.eta_C) * exact_number(cast(float, p.W_C_tr[e]))
                for e in ref.graph.live_edge_ids
            ),
            default=exact_number(),
        )
        * abs(exact_number(p.kappa_Phi_C))
        * b2
        * _norm(dc)
    )
    baseline, baseline_lip = base_factor * retained_upper, base_factor * retained_lip
    if p.tau_C == 0:
        response, response_lip = exact_number(1), exact_number()
    else:
        q = retained_upper / lower**2
        qi = upper**2 / retained_lower
        lq = retained_lip / lower**2 + 2 * retained_upper / lower**3
        lqi = 2 * upper / retained_lower + upper**2 * retained_lip / retained_lower**2
        r = _sqrt_upper(retained_upper / retained_lower)
        lr = r * r * exact_number(p.tau_C) * b2 * retained_lip
        response = qi * r * q
        response_lip = lqi * r * q + qi * lr * q + qi * r * lq
    beta = abs(exact_number(p.zeta_C) * exact_number(p.chi_C))
    margin = 1 - beta * response
    _require(margin > 0, "C CI physical current inverse is not certified on the ball")
    conditioning = (1 + beta * response) / margin
    _require(
        conditioning <= exact_number(ref.profile.params_resolved.solver.conditioning_limit),
        "C CI whole-domain physical conditioning is uncertified",
    )
    current = baseline / margin
    current_lip = baseline_lip / margin + baseline * beta * response_lip / margin**2
    chi = abs(exact_number(p.chi_C))
    flat = chi * response * current / lower
    flat_lip = chi * (
        response * current / lower**2
        + (response_lip * current + response * current_lip) / lower
    )
    return dict(
        flat=flat,
        flat_lip=flat_lip,
        current=current,
        current_lip=current_lip,
        current_inverse=1 / margin,
        conditioning_upper=conditioning,
        selector_gap_lower=gap,
        selector_rank=point.algebra.selector.rank,
        admitted_strata=1,
    )


@dataclass(frozen=True, slots=True)
class CIContractionCertificate:
    """Computed whole-domain sufficient conditions, not a numerical detector."""

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference | None = None
    bounds: FrozenJSONMap = field(init=False)

    def __post_init__(self) -> None:
        domain = _declarations(self.inputs)
        ref = self.inputs.geometry.reference
        _require(
            self.inputs.stage == "pre_read" and self.inputs.geometry == ref.geometry(),
            "CI certification requires reference pre-read inputs",
        )
        composite = ref.profile.params_resolved.realization
        envelope = None
        if isinstance(composite, CIPCParams):
            from .grc_v4_pc import PCEnvelopeCertificate

            # Certify B_2R/current regularity and same-root source over the full
            # compact base chart before any candidate solve is attempted.
            envelope = PCEnvelopeCertificate(self.inputs, self.differential_reference)
        point = _point(self.inputs, self.differential_reference)
        weights = tuple(
            exact_number(cast(float, ref.edge_weights[e])) for e in ref.graph.live_edge_ids
        )
        radius = exact_number(domain.radius)
        lower, upper = (
            min(weights, default=exact_number(1)) - radius,
            max(weights, default=exact_number(1)) + radius,
        )
        _require(lower > 0, "CI ball is not wholly inside the SPD domain")
        _require(
            upper / lower
            <= exact_number(ref.profile.params_resolved.solver.conditioning_limit),
            "CI whole-domain Hodge conditioning is uncertified",
        )
        bounds = (
            _a_read_bounds(point, radius, lower)
            if isinstance(point, CandidateACurrent)
            else _c_read_bounds(point, radius, lower, upper)
        )
        gain = abs(
            exact_number(ref.profile.params_resolved.geometry.kappa_H) * _gain(point)
        )
        displacement = gain * bounds["flat"] ** 2
        contraction = 2 * gain * bounds["flat"] * bounds["flat_lip"]
        if envelope is not None:
            assert isinstance(composite, CIPCParams)
            uniform = envelope.bounds
            kh = abs(exact_number(ref.profile.params_resolved.geometry.kappa_H))
            source_upper = exact_number(cast(str, uniform["source_norm_upper"]))
            displacement = kh * (exact_number(composite.radius) + source_upper)
            contraction = (
                2
                * gain
                * exact_number(cast(str, uniform["flat_norm_upper"]))
                * exact_number(cast(str, uniform["flat_geometry_lipschitz_upper"]))
            )
            bounds.update(
                carrier_radius=exact_number(composite.radius),
                composite_geometry_radius=2 * kh * exact_number(composite.radius),
                uniform_source_upper=source_upper,
                uniform_source_slack=exact_number(composite.radius) - source_upper,
                rho_inst=composite.rho_inst,
                composite_envelope=envelope.bounds,
            )
        _require(
            displacement <= radius, "CI bounded map is not certified to be a self-map"
        )
        _require(contraction < 1, "CI contraction bound must be strictly below one")
        bounds.update(
            radius=radius,
            hodge_lower=lower,
            hodge_upper=upper,
            displacement_upper=displacement,
            contraction_upper=contraction,
            reference_connected=True,
            regular_reduced_root=True,
            norm=JOINT_NORM,
            scope="analytic_local_reference_ball",
        )
        object.__setattr__(
            self,
            "bounds",
            FrozenJSONMap(
                {k: str(v) if is_exact(v) else v for k, v in bounds.items()}
            ),
        )


@dataclass(frozen=True, slots=True)
class CandidateCIRoot:
    """Deterministic reduced fixed point with a fresh literal joint residual.

    Every inner current is solved directly at the current trial Hodge. The
    generated geometry then advances the outer iteration. The selected output
    binds that iteration's actual current and geometry, with no old-root seed.
    """

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference | None = None
    certificate: CIContractionCertificate = field(init=False)
    selected: CITrial = field(init=False)
    evaluations: int = field(init=False)

    def __post_init__(self) -> None:
        before = self.inputs
        domain = _declarations(before)
        certificate = CIContractionCertificate(before, self.differential_reference)
        ref = before.geometry.reference
        params = ref.profile.params_resolved.realization
        assert isinstance(params, (CISolverParams, CIPCParams))
        h = ref.geometry()
        zero = PhysicalFlux(ref.graph, (0.0,) * len(ref.graph.live_edge_ids))
        for index in range(params.iteration_limit):
            seed = replace(
                before,
                geometry=h,
                stage="cipc_trial" if isinstance(params, CIPCParams) else "ci_trial",
                evaluation_index=index,
                trial_current=zero,
            )
            current = _point(seed, self.differential_reference).current
            trial = CITrial(
                replace(seed, trial_current=current), self.differential_reference
            )
            _require(
                trial.point.current == current,
                "CI residual reconstruction changed the eliminated current",
            )
            _in_ball(trial.generated, domain)
            if isinstance(params, CIPCParams):
                from .grc_v4_pc import _ball

                _ball(
                    (x for row in trial.structural_source.increment for x in row),
                    params.radius,
                    "stored same-root source",
                )
            if trial.residual_squared <= exact_number(params.tolerance) ** 2:
                for name, value in (
                    ("certificate", certificate),
                    ("selected", trial),
                    ("evaluations", index + 1),
                ):
                    object.__setattr__(self, name, value)
                return
            h = trial.generated
        raise CIStageError(
            "no_admitted_root",
            "CI iteration limit exhausted without a joint residual pass",
        )

    @property
    def current(self) -> PhysicalFlux:
        return self.selected.point.current

    def to_payload(self) -> dict[str, Any]:
        return dict(
            schema_version="grcv4-ci-root-recipe-v1",
            numerics=CIPC_NUMERICS if self.inputs.current.Z_4 is not None else NUMERICS,
            inputs=self.inputs.to_payload(),
            differential_reference=None
            if self.differential_reference is None
            else self.differential_reference.to_payload(),
        )

    @property
    def identity(self) -> str:
        return _identity("grcv4-ci-root-sha256", self.to_payload())

    @classmethod
    def from_payload(cls, value: object) -> CandidateCIRoot:
        data = _local_payload(
            value,
            {"schema_version", "numerics", "inputs", "differential_reference"},
            "schema_version",
            "grcv4-ci-root-recipe-v1",
        )
        inputs = GeometryStageInputs.from_payload(data["inputs"])
        _require(
            data["numerics"]
            == (CIPC_NUMERICS if inputs.current.Z_4 is not None else NUMERICS),
            "unsupported CI numerical recipe",
        )
        backend = data["differential_reference"]
        return cls(
            inputs,
            None
            if backend is None
            else CandidateADifferentialReference.from_payload(backend),
        )


@dataclass(frozen=True, slots=True)
class ProvisionalCandidateCIStep:
    """Selected CI/CI+PC current, one continuity, ordered writers and readmission.

    Both initial current/reset states and the final state have their own CI
    domain/root admission. The final root is a postcondition, never fed back
    into this beat's continuity or writer. Zero duration admits algebraic
    state but advances no resource, history, clock or step index. All values
    are detached; lifecycle authentication and atomic publication are pending.
    """

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference | None = None
    root: CandidateCIRoot = field(init=False)
    reset_root: CandidateCIRoot = field(init=False)
    resource: ProvisionalResourceStep = field(init=False)
    writer: CandidateAWriter | None = field(init=False)
    restart: CandidateCIRoot = field(init=False)
    next_inputs: GeometryStageInputs = field(init=False)
    carrier_writes: int = field(init=False)

    def __post_init__(self) -> None:
        from .grc_v4_step import (
            CurrentSelection,
            ProvisionalResourceStep,
            ResourceBoundaryError,
            _resource_charge,
        )

        before = self.inputs
        _declarations(before)
        ref = before.geometry.reference
        params = ref.profile.params_resolved.realization
        if (
            ref.profile.identity_payload.candidate == "A"
            and ref.profile.params_resolved.lifecycle.history_policy_id
            not in ADMITTED_HISTORY_POLICIES
        ):
            raise ValueError("unimplemented A retained-history writer policy")
        _require(
            before.stage == "pre_read" and before.geometry == ref.geometry(),
            "CI step requires fresh reference prestate",
        )
        _resource_charge(before, VertexScalar(ref.graph, before.current.C), "admission")
        _resource_charge(before, VertexScalar(ref.graph, before.reset.C), "admission")
        if before.dt != 0 and before.step_index >= 2**53 - 1:
            raise ResourceBoundaryError(
                "admission",
                "domain_failure",
                "CI step index would exceed the safe integer domain",
            )
        try:
            next_time = float(exact_number(before.time) + exact_number(before.dt))
        except OverflowError as exc:
            raise ResourceBoundaryError(
                "admission", "nonfinite_value", "CI clock overflow"
            ) from exc
        if not math.isfinite(next_time):
            raise ResourceBoundaryError(
                "admission", "nonfinite_value", "CI clock overflow"
            )
        stage: OperationStage = "pre_read_reconstruction"
        try:
            reset_root = CandidateCIRoot(
                replace(before, current=before.reset), self.differential_reference
            )
            stage = "candidate_solve"
            root = CandidateCIRoot(before, self.differential_reference)
            selection = (
                None
                if before.dt == 0
                else CurrentSelection(root.selected.inputs, "valid_root", root.current)
            )
            stage = "continuity"
            resource = ProvisionalResourceStep(before, selection)
            writer = None
            if before.dt == 0:
                following, restart = before, root
            else:
                if isinstance(root.selected.point, CandidateACurrent):
                    stage = "history_write"
                    writer = CandidateAWriter(root.selected.point, resource)
                    final = writer.authority.state
                else:
                    final = resource.consume(
                        expected_prestate=before, expected_selection=selection
                    )
                if isinstance(params, CIPCParams):
                    from .grc_v4_pc import _ball, scalar_zoh

                    stage = "history_write"
                    assert before.current.Z_4 is not None
                    source = tuple(
                        x
                        for row in root.selected.structural_source.increment
                        for x in row
                    )
                    z = scalar_zoh(before.current.Z_4, source, before.dt, params.tau_PC)
                    _ball(z, params.radius, "written carrier")
                    final = GRCV4AuthoritativeState(final.C, final.W_A, z)
                stage = "final_reconstruction"
                following = replace(
                    before,
                    current=final,
                    time=next_time,
                    step_index=before.step_index + 1,
                )
                restart = CandidateCIRoot(
                    replace(following, dt=0), self.differential_reference
                )
        except (
            CIStageError,
            CandidateAStageError,
            CandidateCStageError,
            GeometryDomainError,
            NonfiniteGeometryError,
            OverflowError,
        ) as exc:
            disposition = getattr(exc, "disposition", "domain_failure")
            if disposition == "nonfinite" or isinstance(
                exc, (NonfiniteGeometryError, OverflowError)
            ):
                raise ResourceBoundaryError(stage, "nonfinite_value", str(exc)) from exc
            if disposition == "singular":
                raise ResourceBoundaryError(stage, "singular_solver", str(exc)) from exc
            if disposition == "conditioning_failure":
                raise ResourceBoundaryError(
                    stage, "conditioning_failure", str(exc)
                ) from exc
            if disposition == "no_admitted_root":
                raise ResourceBoundaryError(
                    stage, "no_admitted_root", str(exc)
                ) from exc
            raise ResourceBoundaryError(stage, "domain_failure", str(exc)) from exc
        for name, value in (
            ("root", root),
            ("reset_root", reset_root),
            ("resource", resource),
            ("writer", writer),
            ("restart", restart),
            ("next_inputs", following),
            ("carrier_writes", int(before.dt > 0 and isinstance(params, CIPCParams))),
        ):
            object.__setattr__(self, name, value)

    def to_payload(self) -> dict[str, Any]:
        return dict(
            schema_version="grcv4-ci-step-recipe-v1",
            numerics=CIPC_NUMERICS if self.inputs.current.Z_4 is not None else NUMERICS,
            inputs=self.inputs.to_payload(),
            differential_reference=None
            if self.differential_reference is None
            else self.differential_reference.to_payload(),
        )

    @classmethod
    def from_payload(cls, value: object) -> ProvisionalCandidateCIStep:
        data = _local_payload(
            value,
            {"schema_version", "numerics", "inputs", "differential_reference"},
            "schema_version",
            "grcv4-ci-step-recipe-v1",
        )
        inputs = GeometryStageInputs.from_payload(data["inputs"])
        _require(
            data["numerics"]
            == (CIPC_NUMERICS if inputs.current.Z_4 is not None else NUMERICS),
            "unsupported CI step recipe",
        )
        backend = data["differential_reference"]
        return cls(
            inputs,
            None
            if backend is None
            else CandidateADifferentialReference.from_payload(backend),
        )
