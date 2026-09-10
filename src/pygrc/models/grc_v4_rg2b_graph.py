"""Graph-general RG2b certificate and finite matrix-section arithmetic.

The ordinary-step owner remains grc_v4_rg2b. All charts are fixed profile
configuration; neither certificates nor numerical iterates are causal state.
State coordinates use the sup norm, geometry and K4 use Frobenius norms.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction as F
from typing import Any, cast

from .grc_v4_candidate_a import CandidateACurrent, CandidateADifferentialReference
from .grc_v4_candidate_c import (
    CandidateCCurrent,
    _c_exact,
    _c_mm,
    _c_inverse,
    _c_transpose,
)
from .grc_v4_ci import (
    _Interval,
    _iv,
    _iexp,
    _im,
    _imm,
    _norm,
    _opnorm,
    _sqrt_upper,
    _analytic_residual,
)
from .grc_v4_geometry import GeometryStageInputs, GRCV4Geometry, OneFormHodge, _computed
from .grc_v4_profile import CandidateAParams, RG2bParams
from .grc_v4_state import GRCV4AuthoritativeState, FrozenJSONMap
from .grc_v4_rg2b import RG2bDomain, RG2bStageError, _require, _ilog, _cutoff

EXTENSION = "rg2b_graph_cubic_completion_v1:"
APPROXIMATION = "rg2b_matrix_ball_graph_transform_160bit_inverse64_depth16_v1"
ERROR_NORM = "rg2b_hodge_frobenius_v1"
CONTAINMENT = "rg2b_derived_graph_compact_linfty_C_W_certificate_v1"


@dataclass(frozen=True, slots=True)
class RG2bGraphDomain(RG2bDomain):
    @property
    def identity(self) -> str:
        return EXTENSION + ":".join(
            getattr(self, n).hex() for n in self.__dataclass_fields__
        )

    @classmethod
    def from_identity(cls, value: object) -> RG2bGraphDomain:
        _require(
            type(value) is str and value.startswith(EXTENSION),
            "unknown graph completion",
        )
        assert isinstance(value, str)
        try:
            result = cls(
                *(float.fromhex(x) for x in value[len(EXTENSION) :].split(":"))
            )
        except (ValueError, TypeError, OverflowError) as exc:
            raise RG2bStageError("invalid graph completion coordinates") from exc
        _require(result.identity == value, "noncanonical graph completion")
        return result


def rounded_upper(value: F) -> F:
    """Outward 160-bit bound; prevents unbounded rational diagnostic strings."""
    _require(value >= 0, "negative RG2b error or norm bound")
    return _Interval(F(), value).hi


def centers(inputs: GeometryStageInputs, d: RG2bDomain) -> tuple[float, ...]:
    graph = inputs.geometry.reference.graph
    return (d.center_C,) * len(graph.live_node_ids) + (
        (d.center_W,) * len(graph.live_edge_ids)
        if inputs.current.W_A is not None
        else ()
    )


def coordinates(state: GRCV4AuthoritativeState) -> tuple[F, ...]:
    return tuple(map(F, state.C + (() if state.W_A is None else state.W_A)))


def descriptor_operators(backend: CandidateADifferentialReference) -> tuple[Any, ...]:
    """Exact WLS linear maps for interval-valued post-continuity resources.

    This is the certificate's linear coefficient form of the existing WLS
    equation, not a second native descriptor backend or admission policy.
    """
    graph, dim = backend.graph, backend.dimension
    n = len(graph.live_node_ids)
    result = []
    for i, node in enumerate(graph.live_node_ids):
        normal = [
            [F(backend.regularization) * int(k == column) for column in range(dim)]
            for k in range(dim)
        ]
        rhs = [[F() for _ in range(n)] for _ in range(dim)]
        for edge in graph.oriented_edges:
            if node not in (edge.tail_node_id, edge.head_node_id):
                continue
            other = (
                edge.head_node_id if node == edge.tail_node_id else edge.tail_node_id
            )
            j = graph.node_index(other)
            delta = tuple(
                F(y) - F(x)
                for x, y in zip(backend.positions[i], backend.positions[j], strict=True)
            )
            weight = F(cast(float, backend.reference_weights[edge.edge_id]))
            for k in range(dim):
                rhs[k][j] += weight * delta[k]
                rhs[k][i] -= weight * delta[k]
                for column in range(dim):
                    normal[k][column] += weight * delta[k] * delta[column]
        result.append(
            _c_mm(_c_inverse(tuple(map(tuple, normal))), tuple(map(tuple, rhs)))
        )
    return tuple(result)


@dataclass(frozen=True, slots=True)
class GraphAlgebra:
    incidence: Any
    descriptors: tuple[Any, ...]


def certificate(
    inputs: GeometryStageInputs,
    backend: CandidateADifferentialReference | None,
    d: RG2bGraphDomain,
) -> dict[str, Any]:
    ref, graph = inputs.geometry.reference, inputs.geometry.reference.graph
    p = ref.profile.params_resolved.candidate
    n, m = len(graph.live_node_ids), len(graph.live_edge_ids)
    _require(n > 0 and m > 0, "RG2b requires nonempty resource and structural spaces")
    b = _c_exact(graph.incidence)
    bt = _c_transpose(b)
    bn, b2, sn = _opnorm(b), _opnorm(_c_mm(bt, b)), _sqrt_upper(F(n))
    r, dt = F(d.h_radius), F(d.beat_dt)
    weights = tuple(F(cast(float, ref.edge_weights[e])) for e in graph.live_edge_ids)
    lower, upper = min(weights) - r, max(weights) + r
    limit = F(ref.profile.params_resolved.solver.conditioning_limit)
    _require(
        lower > 0 and upper / lower <= limit,
        "RG2b graph Hodge ball is not SPD/conditioning certified",
    )
    cmax, crad = F(d.center_C) + F(d.outer), sn * F(d.outer)
    dc, dcx = _opnorm(bt) * crad, _opnorm(bt) * sn
    descriptors: tuple[Any, ...] = ()
    extra: dict[str, Any] = {}
    rank = 0
    if isinstance(p, CandidateAParams):
        assert backend is not None
        CandidateACurrent(inputs, backend)
        descriptors = descriptor_operators(backend)
        gd = max((_opnorm(a) for a in descriptors), default=F())
        wlo, wup = F(d.center_W) - F(d.outer), F(d.center_W) + F(d.outer)
        eta, kc, kah = abs(F(p.eta)), abs(F(p.kappa_c)), abs(F(p.kappa_Ah))
        ah = kc * wup + kah * r
        j0 = eta * wup * b2 * ah * dc
        j0x = eta * b2 * (ah * dc + wup * (kc * dc + ah * dcx))
        j0h = eta * wup * b2 * kah * dc
        contrast, contrast_x = 2 * gd * crad, 2 * gd * sn
        alpha, beta, gamma = abs(F(p.alpha)), abs(F(p.beta)), abs(F(p.gamma))
        exponent = (2 * alpha * cmax + beta * contrast**2 + gamma * j0**2) / 2
        _require(
            _iexp(_iv(-exponent)).lo > F(p.W_floor),
            "RG2b A pre-read floor chart is not strictly inactive",
        )
        ex = alpha + beta * contrast * contrast_x + gamma * j0 * j0x
        eh = gamma * j0 * j0h
        qx, qh = 1 / (2 * wlo) + ex / 2, eh / 2
        zchi = abs(F(p.zeta_A) * F(p.chi_A))
        margin = 1 - zchi
        _require(margin > 0, "RG2b A whole-chart current inverse is uncertified")
        jmax = j0 / margin
        jx, jh = (
            j0x / margin + j0 * zchi * qx / margin**2,
            j0h / margin + j0 * zchi * qh / margin**2,
        )
        chi, zeta = abs(F(p.chi_A)), abs(F(p.zeta_A))
        flat = chi * jmax / lower
        flatx = chi * (qx * jmax + jx) / lower
        flath = chi * (jmax / lower**2 + (qh * jmax + jh) / lower)
        response = F(1)
        next_radius = crad + dt * bn * jmax
        next_contrast = 2 * gd * next_radius
        next_x, next_h = sn + dt * bn * jx, dt * bn * jh
        writer_exponent = (
            2 * alpha * (cmax + dt * bn * jmax)
            + beta * next_contrast**2
            + gamma * jmax**2
        ) / 2
        _require(
            _iexp(_iv(-writer_exponent)).lo > F(p.W_floor),
            "RG2b A writer floor chart is not strictly inactive",
        )
        vx = (
            alpha * (1 + dt * bn * jx)
            + beta * next_contrast * 2 * gd * next_x
            + gamma * jmax * jx
        )
        vh = (
            alpha * dt * bn * jh
            + beta * next_contrast * 2 * gd * next_h
            + gamma * jmax * jh
        )
        fraction = (_iv(1) - _iexp(_iv(-dt / F(p.tau_A)))).hi
        logw = max(_ilog(_iv(wlo)).magnitude, _ilog(_iv(wup)).magnitude)
        delta_exp = _iexp(_iv(fraction * (writer_exponent + logw))).hi
        wm = wup * (delta_exp - 1)
        wx = delta_exp - 1 + wup * delta_exp * fraction * (vx + 1 / wlo)
        wh = wup * delta_exp * fraction * vh
        fm, fx, fh = (
            max(dt * bn * jmax, wm),
            max(dt * bn * jx, wx),
            max(dt * bn * jh, wh),
        )
        extra.update(
            descriptor_operator_upper=gd,
            pre_read_exponent_upper=exponent,
            writer_exponent_upper=writer_exponent,
        )
    else:
        point = CandidateCCurrent(inputs)
        rank = point.algebra.selector.rank
        stiffness = _c_mm(_c_mm(b, _c_exact(ref.pairings.one_form.matrix)), bt)
        shifted = tuple(
            tuple(x - (F(p.Lambda_C) if i == j else 0) for j, x in enumerate(row))
            for i, row in enumerate(stiffness)
        )
        from .grc_v4_candidate_c import CandidateCStageError

        try:
            gap = 1 / _opnorm(_c_inverse(shifted)) - b2 * r
        except CandidateCStageError as exc:
            if exc.disposition != "singular":
                raise
            raise RG2bStageError("RG2b reference selector lies on cutoff") from exc
        _require(gap > 0, "RG2b whole-ball selector stratum is uncertified")
        de = _iexp(_iv(abs(F(p.kappa_M_C)) / 2)).hi
        ml, mu = lower / de**2, upper * de**2
        _require(mu / ml <= limit, "RG2b retained Hodge conditioning is uncertified")
        dx = de * abs(F(p.kappa_M_C)) * sn / (2 * F(p.C_ref))
        dh = de * abs(F(p.kappa_M_C)) * (2 * b2 * sn * cmax / gap) / (2 * F(p.C_ref))
        mx, mh = 2 * de * upper * dx, de**2 + 2 * de * upper * dh
        q, qi = mu / lower**2, upper**2 / ml
        resolvent = _sqrt_upper(mu / ml)
        response = F(1) if p.tau_C == 0 else qi * resolvent * q

        def response_lip(dm: F, h_change: bool) -> F:
            if p.tau_C == 0:
                return F()
            lq = dm / lower**2 + (2 * mu / lower**3 if h_change else 0)
            lqi = upper**2 * dm / ml**2 + (2 * upper / ml if h_change else 0)
            lr = resolvent**2 * F(p.tau_C) * b2 * dm
            return lqi * resolvent * q + qi * lr * q + qi * resolvent * lq

        rx, rh = response_lip(mx, False), response_lip(mh, True)
        mobility = max(
            abs(F(p.eta_C) * F(cast(float, p.W_C_tr[e])) * F(p.kappa_Phi_C))
            for e in graph.live_edge_ids
        )
        j0, j0x, j0h = (
            mobility * b2 * mu * dc,
            mobility * b2 * (mx * dc + mu * dcx),
            mobility * b2 * mh * dc,
        )
        zchi = abs(F(p.zeta_C) * F(p.chi_C)) * response
        margin = 1 - zchi
        _require(
            margin > 0, "RG2b C whole-chart physical current inverse is uncertified"
        )
        coupling = abs(F(p.zeta_C) * F(p.chi_C))
        jmax = j0 / margin
        jx, jh = (
            j0x / margin + j0 * coupling * rx / margin**2,
            j0h / margin + j0 * coupling * rh / margin**2,
        )
        chi, zeta = abs(F(p.chi_C)), abs(F(p.zeta_C))
        flat = chi * response * jmax / lower
        flatx = chi * (rx * jmax + response * jx) / lower
        flath = chi * (response * jmax / lower**2 + (rh * jmax + response * jh) / lower)
        fm, fx, fh = dt * bn * jmax, dt * bn * jx, dt * bn * jh
        extra.update(selector_gap_lower=gap, physical_response_upper=response)
    _require(
        (1 + zchi) / margin <= limit,
        "RG2b whole-chart current conditioning is uncertified",
    )
    _require(
        F(d.center_C) - F(d.outer) > dt * bn * jmax,
        "RG2b outer-chart continuity leaves positive resources",
    )
    gm, gx, gh = zeta * flat**2, 2 * zeta * flat * flatx, 2 * zeta * flat * flath
    cut = F(3 * (n + (m if isinstance(p, CandidateAParams) else 0)), 2) / (
        F(d.outer) - F(d.core)
    )
    fx, gx = fx + cut * fm, gx + cut * gm
    fm, fx, fh, gm, gx, gh = map(rounded_upper, (fm, fx, fh, gm, gx, gh))
    lip, kh = (
        F(d.section_lipschitz),
        abs(F(ref.profile.params_resolved.geometry.kappa_H)),
    )
    ell = rounded_upper(fx + fh * lip)
    _require(ell < 1, "RG2b extended graph base map is not uniformly invertible")
    inv = rounded_upper(1 / (1 - ell))
    _require(
        fm <= F(d.core) - F(d.inner), "RG2b graph K_minus containment is uncertified"
    )
    _require(kh * gm <= r, "RG2b graph transform exceeds section value radius")
    _require(
        kh * (gx + gh * lip) * inv <= lip,
        "RG2b graph Lipschitz self-map is uncertified",
    )
    contraction = rounded_upper(kh * (gh + (gx + gh * lip) * inv * fh))
    _require(contraction < 1, "RG2b matrix graph transform is not contractive")
    bounds = dict(
        source_upper=gm,
        source_X_lipschitz=gx,
        source_h_lipschitz=gh,
        base_displacement_upper=fm,
        base_X_lipschitz=fx,
        base_h_lipschitz=fh,
        inverse_displacement_lipschitz=ell,
        inverse_lipschitz=inv,
        contraction_upper=contraction,
        typed_geometry_gain=kh,
        section_lipschitz=lip,
        section_radius=r,
        cutoff_lipschitz=cut,
        current_upper=jmax,
        current_inverse_upper=1 / margin,
        flat_upper=flat,
        flat_current_operator_upper=chi * response / lower,
        source_gain=zeta,
        **extra,
    )
    return dict(
        domain=d,
        bounds=FrozenJSONMap(
            {
                k: str(
                    1 / rounded_upper(1 / v)
                    if k == "selector_gap_lower"
                    else rounded_upper(v)
                )
                for k, v in bounds.items()
            }
        ),
        selector_rank=rank,
        graph_data=GraphAlgebra(b, descriptors),
    )


def point_maps(
    cert: Any, x: tuple[F, ...], h: Any, point: Any = None
) -> tuple[Any, Any, F, F]:
    """Enclose the real candidate maps using native-current residual bounds.

    The existing CI analytic residual encloses the complete A/C equations,
    including the C spectral projector and noncommuting physical response.
    A verified current inverse converts its residual to a current error.
    """
    ref, d = cert.inputs.geometry.reference, cert.domain
    n, m = len(ref.graph.live_node_ids), len(ref.graph.live_edge_ids)
    p = ref.profile.params_resolved.candidate
    if point is None:
        state = GRCV4AuthoritativeState(
            tuple(_computed(float(v)) for v in x[:n]),
            tuple(_computed(float(v)) for v in x[n:])
            if isinstance(p, CandidateAParams)
            else None,
            None,
        )
        geometry = GRCV4Geometry(ref, OneFormHodge(ref.graph, h))
        selected = replace(
            cert.inputs, current=state, geometry=geometry, stage="rg2b_section"
        )
        point = (
            CandidateACurrent(selected, cert.differential_reference)
            if isinstance(p, CandidateAParams)
            else CandidateCCurrent(selected)
        )
    _require(
        coordinates(point.inputs.current) == x
        and point.inputs.geometry.one_form_hodge.matrix == h
        and point.inputs.geometry.reference == ref,
        "RG2b point enclosure requires the same represented state and geometry",
    )
    residual, geometry_residual = _analytic_residual(point, point.current)
    bounds = {k: F(v) for k, v in cert.bounds.items()}
    je = _norm(v.magnitude for v in residual) * bounds["current_inverse_upper"]
    j = tuple(_Interval(F(v) - je, F(v) + je) for v in point.current.values)
    dt = F(d.beat_dt)
    f = tuple(
        -dt * row[0]
        for row in _imm(_im(cert.graph_data.incidence), tuple((v,) for v in j))
    )
    final_c = tuple(_iv(v) + dv for v, dv in zip(x[:n], f, strict=True))
    if isinstance(p, CandidateAParams):
        descriptors = tuple(
            _imm(_im(op), tuple((v,) for v in final_c))
            for op in cert.graph_data.descriptors
        )
        fraction = _iv(1) - _iexp(_iv(-dt / F(p.tau_A)))
        writer = []
        for k, edge in enumerate(ref.graph.oriented_edges):
            u, v = (
                ref.graph.node_index(edge.tail_node_id),
                ref.graph.node_index(edge.head_node_id),
            )
            contrast = tuple(
                a[0] - b[0] for a, b in zip(descriptors[u], descriptors[v], strict=True)
            )
            square = sum((a * a for a in contrast), _iv(0))
            exponent = (
                -(
                    F(p.alpha) * (final_c[u] + final_c[v])
                    + F(p.beta) * square
                    + F(p.gamma) * j[k] * j[k]
                )
                / 2
            )
            w = _iv(x[n + k])
            writer.append(w * (_iexp(fraction * (exponent - _ilog(w))) - 1))
        f += tuple(writer)
    kh = abs(F(ref.profile.params_resolved.geometry.kappa_H))
    dv = bounds["flat_current_operator_upper"] * je
    ge = kh * bounds["source_gain"] * (2 * bounds["flat_upper"] * dv + dv * dv)
    generated = tuple(
        tuple(_iv(h[i][k]) - geometry_residual[i][k] for k in range(m))
        for i in range(m)
    )
    return f, generated, je, ge


@dataclass(frozen=True, slots=True)
class MatrixBall:
    center: Any
    error: F


def matrix_ball(intervals: Any, extra: F = F()) -> MatrixBall:
    m = len(intervals)
    midpoint = [[0.0] * m for _ in range(m)]
    for i in range(m):
        for j in range(i, m):
            lo, hi = (
                max(intervals[i][j].lo, intervals[j][i].lo),
                min(intervals[i][j].hi, intervals[j][i].hi),
            )
            _require(lo <= hi, "symmetric graph-section enclosures do not intersect")
            midpoint[i][j] = midpoint[j][i] = _computed(float((lo + hi) / 2))
    error = _norm(
        max(abs(F(midpoint[i][j]) - v.lo), abs(F(midpoint[i][j]) - v.hi))
        for i, row in enumerate(intervals)
        for j, v in enumerate(row)
    )
    return MatrixBall(tuple(map(tuple, midpoint)), rounded_upper(error + extra))


def section(cert: Any) -> dict[str, Any]:
    ref, d = cert.inputs.geometry.reference, cert.domain
    params = cast(RG2bParams, ref.profile.params_resolved.realization)
    x = coordinates(cert.inputs.current)
    center = centers(cert.inputs, d)
    _require(
        all(abs(v - F(c)) <= F(d.core) for v, c in zip(x, center, strict=True)),
        "RG2b section query is outside K",
    )
    href = ref.pairings.one_form.matrix
    bounds = {k: F(v) for k, v in cert.bounds.items()}
    kh = bounds["typed_geometry_gain"]
    tolerance = F(params.error_tolerance)
    sensitivity = kh * (
        bounds["source_X_lipschitz"]
        + bounds["source_h_lipschitz"] * bounds["section_lipschitz"]
    )
    guard = tolerance / (32 * sensitivity) if sensitivity else F()
    neutral = kh == 0 or bounds["source_upper"] == 0
    calls = 0

    def evaluate(level: int, target: tuple[F, ...]) -> MatrixBall:
        nonlocal calls
        if level == 0 or neutral:
            return MatrixBall(href, F())
        mid = target
        for _ in range(64):
            calls += 1
            _require(
                calls <= params.iteration_limit,
                "RG2b deterministic evaluation budget exhausted",
            )
            cutoff = F(1)
            for value, c in zip(mid, center, strict=True):
                cutoff *= _cutoff(value, c, d)
            if cutoff == 0:
                inverse_error = (
                    max(abs(v - t) for v, t in zip(mid, target, strict=True))
                    * bounds["inverse_lipschitz"]
                )
                if inverse_error <= guard:
                    return MatrixBall(href, sensitivity * inverse_error)
                mid = target
                continue
            gamma = evaluate(level - 1, mid)
            _require(
                _norm(
                    F(a) - F(b)
                    for row, old in zip(gamma.center, href, strict=True)
                    for a, b in zip(row, old, strict=True)
                )
                <= F(d.h_radius),
                "rounded graph-section iterate leaves the Hodge ball",
            )
            f, g, _, ge = point_maps(cert, mid, gamma.center)
            fe = bounds["base_h_lipschitz"] * gamma.error
            f = tuple(cutoff * _Interval(v.lo - fe, v.hi + fe) for v in f)
            inverse_error = (
                max(
                    (_iv(v) - t + dv).magnitude
                    for v, t, dv in zip(mid, target, f, strict=True)
                )
                * bounds["inverse_lipschitz"]
            )
            if inverse_error <= guard:
                generated = tuple(
                    tuple(
                        _iv(base) + cutoff * (v - base)
                        for v, base in zip(row, old, strict=True)
                    )
                    for row, old in zip(g, href, strict=True)
                )
                return matrix_ball(
                    generated,
                    cutoff * (ge + kh * bounds["source_h_lipschitz"] * gamma.error)
                    + sensitivity * inverse_error,
                )
            mid = tuple(
                F(_computed(float(t - (v.lo + v.hi) / 2)))
                for t, v in zip(target, f, strict=True)
            )
        raise RG2bStageError("RG2b graph inverse enclosure unresolved")

    chosen = None
    for level in range(17):
        tail = F() if neutral else F(d.h_radius) * bounds["contraction_upper"] ** level
        if tail > tolerance / 4:
            continue
        value = evaluate(level, x)
        error = rounded_upper(value.error + tail)
        _require(
            error <= tolerance,
            "RG2b matrix approximation/error tolerance is uncertified",
        )
        chosen = (level, value, error)
        break
    _require(
        chosen is not None, "RG2b graph-transform depth budget cannot certify tolerance"
    )
    assert chosen is not None
    level, value, error = chosen
    _require(
        _norm(
            F(a) - F(b)
            for row, old in zip(value.center, href, strict=True)
            for a, b in zip(row, old, strict=True)
        )
        <= F(d.h_radius),
        "stored graph section exceeds its Hodge ball",
    )
    return dict(
        geometry=GRCV4Geometry(ref, OneFormHodge(ref.graph, value.center)),
        enclosure=("frobenius_ball_about_stored_geometry", str(error)),
        error_upper=str(error),
        levels=level,
        evaluations=calls,
    )


def native_bridge(
    section: Any, point: Any, following: GeometryStageInputs, generated: GRCV4Geometry
) -> tuple[F, F, F, F]:
    cert = section.certificate
    x, y = coordinates(cert.inputs.current), coordinates(following.current)
    f, g, je, ge = point_maps(cert, x, section.geometry.one_form_hodge.matrix, point)
    xe = max(
        (_iv(actual) - old - delta).magnitude
        for actual, old, delta in zip(y, x, f, strict=True)
    )
    he = (
        _norm(
            (_iv(actual) - v).magnitude
            for row, other in zip(g, generated.one_form_hodge.matrix, strict=True)
            for v, actual in zip(row, other, strict=True)
        )
        + ge
    )
    return je, xe, he, _norm(point.current.values) + je
