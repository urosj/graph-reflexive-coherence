"""Native A_RG2b signed C/scaled-log-W completion and certified finite section.

Only C/W are authority. Four coupled inverse levels include the fresh-resource
W writer. Binary64 proposals are recertified in ExactScalar outward intervals;
physical resources/history are never clipped to admit a failed transition.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from . import grc_v4_numerics as numerics
from .grc_9_v4_rg2b import infinity
from .grc_9_v4_topology import GRC9V4CandidateADifferentialReference
from .grc_v4_candidate_a import CandidateACurrent
from .grc_v4_candidate_c import _c_components
from .grc_v4_ci import _iexp, _iinverse, _im, _imm, _Interval, _iv, _norm
from .grc_v4_codec import _dependency
from .grc_v4_exact import ExactScalar
from .grc_v4_exact import exact_number as Q
from .grc_v4_geometry import GRCV4Geometry, OneFormHodge
from .grc_v4_rg2b import RG2bDomain, RG2bStageError, _ilog, _require
from .grc_v4_state import FrozenJSONMap

EXTENSION = "grc9v4_a_rg2b_signed_argument_completion_v1"
APPROXIMATION = "grc9v4_a_rg2b_chain4_sweeps18_binary64_interval160_v1"
ERROR_NORM = "grc9v4_rg2b_hodge_induced_infinity_v1"
CONTAINMENT = "grc9v4_a_rg2b_signed_tree17_global_certificate_v1"
DEPTH, SWEEPS = 4, 18


@dataclass(frozen=True, slots=True)
class NativeARG2bDomain(RG2bDomain):
    """C chart matches signed C; scaled-log Y radii are 5/8, 3/4 and 1."""

    def __post_init__(self) -> None:
        expected = (2.0, 1.0, 2.25, 2.5, 3.0, 2**-12, 2**-10, 2**-12)
        _require(
            tuple(getattr(self, k) for k in self.__dataclass_fields__) == expected
            and all(type(getattr(self, k)) is float for k in self.__dataclass_fields__),
            "native A_RG2b requires its exact signed completion coordinates",
        )

    @property
    def identity(self) -> str:
        return EXTENSION

    @classmethod
    def from_identity(cls, value: object) -> NativeARG2bDomain:
        _require(
            type(value) is str and value == EXTENSION, "unknown signed A completion"
        )
        return cls(2.0, 1.0, 2.25, 2.5, 3.0, 2**-12, 2**-10, 2**-12)


def coordinates(state: Any) -> tuple[Any, ...]:
    _require(
        state.W_A is not None and all(Q(w) > 0 for w in state.W_A),
        "positive A history required",
    )
    return tuple(_iv(c) for c in state.C) + tuple(
        512 * _ilog(_iv(w)) for w in state.W_A
    )


def admit(state: Any, *, ordinary: bool) -> tuple[Any, ...]:
    x = coordinates(state)
    c_radius, y_radius = (Q(9, 4), Q(5, 8)) if ordinary else (Q(5, 2), Q(3, 4))
    _require(
        all((_iv(c) - 2).magnitude <= c_radius for c in state.C)
        and all(v.magnitude <= y_radius for v in x[len(state.C) :]),
        "RG2b current/reset ordinary prestate is outside K_minus"
        if ordinary
        else "RG2b section query is outside K",
    )
    return x


@dataclass(frozen=True, slots=True)
class Algebra:
    incidence: Any
    gram: Any
    mask: Any
    rows: Any
    ends: Any


def certificate(inputs: Any, backend: Any, domain: NativeARG2bDomain) -> dict[str, Any]:
    """Exact global A estimates, including normalized row and writer slopes."""
    ref = inputs.geometry.reference
    graph, p = ref.graph, ref.profile.params_resolved.candidate
    n, m = len(graph.live_node_ids), len(graph.live_edge_ids)
    _require(
        type(backend) is GRC9V4CandidateADifferentialReference
        and graph.port_graph is not None,
        "native A fixed-port owner required",
    )
    _require(ref.profile.identity_payload.profile_family_id == "A_RG2b", "A_RG2b only")
    _require(
        2 <= n <= 17
        and m == n - 1
        and len(_c_components(graph)) == 1
        and all(e.tail_node_id != e.head_node_id for e in graph.oriented_edges),
        "signed A completion requires a connected tree with at most 17 vertices",
    )
    _require(
        all(
            getattr(p, k) == v
            for k, v in {
                "eta": 1,
                "kappa_c": 1,
                "W_floor": 0.5,
                "alpha": 2**-24,
                "beta": 2**-24,
                "gamma": 2**-24,
                "kappa_Ah": 0.5,
                "chi_A": 1 / 16,
                "zeta_A": 0.5,
                "tau_A": 1,
            }.items()
        )
        and ref.profile.params_resolved.geometry.kappa_H == 0.5
        and all(v == 1 for v in ref.edge_weights.values())
        and all(v == 0 for row in ref.K4_base for v in row),
        "signed A completion parameter/reference binding mismatch",
    )
    b = numerics.exact_matrix(graph.incidence)
    gram = numerics.matmul(numerics.transpose(b), b)
    ends = [{e.tail_node_id, e.head_node_id} for e in graph.oriented_edges]
    mask = tuple(tuple(Q(len(u & v), 2) for v in ends) for u in ends)
    _require(
        infinity(b) <= 9 and infinity(gram) <= 10 and infinity(mask) <= 5,
        "signed A completion graph norm hypotheses fail",
    )
    rows: list[list[list[tuple[int, int]]]] = [[[] for _ in range(3)] for _ in range(n)]
    edge_ends = []
    for k, e in enumerate(graph.port_graph.edges):
        u, v = graph.node_index(e.tail.node_id), graph.node_index(e.head.node_id)
        edge_ends.append((u, v))
        rows[u][(e.tail.port - 1) // 3].append((k, v))
        rows[v][(e.head.port - 1) // 3].append((k, u))
    rho, lip, dt, kh, eps = Q(1, 4096), Q(1, 1024), Q(1, 4096), Q(1, 2), Q(1, 2**24)
    _require(
        (1 + rho) / (1 - rho)
        <= Q(ref.profile.params_resolved.solver.conditioning_limit),
        "signed Hodge ball conditioning not certified",
    )
    CandidateACurrent(inputs, backend)
    scale, span, hinv = Q(512), Q(6), 1 / (1 - rho)
    wl, wu = 1 - 1 / scale, 1 / (1 - 1 / scale)
    j0 = wu * 10 * (wu + kh * rho) * span
    j0x = wu * 10 * ((wu + kh * rho) * 2 + (2 * wu + kh * rho) * span / scale)
    j0h = wu * kh * 10 * span
    row_x = 2 + 2 * span / scale
    emax, emin = eps * (10 + 12 * span**2 + j0**2) / 2, -eps
    gl, gu = 1 - emax, 1 / (1 + emin)
    _require(gl > Q(1, 2) and -emin < 1, "A read floor/exp bound unresolved")
    qmax = max(abs((wl - gu) / (wl + gu)), abs((wu - gl) / (wu + gl)))
    ex, eh = eps * (2 + 24 * span * row_x + 2 * j0 * j0x) / 2, eps * j0 * j0h
    qx, qh = (1 / scale + ex) / 2, eh / 2
    chi, zeta = Q(1, 16), Q(1, 2)
    theta = chi * zeta * qmax
    j = j0 / (1 - theta)
    jx, jh = (
        (j0x + chi * zeta * qx * j) / (1 - theta),
        (j0h + chi * zeta * qh * j) / (1 - theta),
    )
    causal, cx, ch = (
        chi * qmax * j,
        chi * (qx * j + qmax * jx),
        chi * (qh * j + qmax * jh),
    )
    advance = dt * 9 * j
    post_span = span + 2 * advance
    post_x, post_h = 1 + dt * 9 * jx, dt * 9 * jh
    post_row_x, post_row_h = 2 * post_x + 2 * post_span / scale, 2 * post_h
    writer_emax = eps * (2 * (5 + advance) + 12 * post_span**2 + j**2) / 2
    writer_emin = eps * (-1 - advance)
    _require(1 - writer_emax > Q(1, 2), "A writer floor bound unresolved")
    writer_ex = eps * (2 * post_x + 24 * post_span * post_row_x + 2 * j * jx) / 2
    writer_eh = eps * (2 * post_h + 24 * post_span * post_row_h + 2 * j * jh) / 2
    ax, ah = (
        max(dt * 9 * jx, dt * (1 + scale * writer_ex)),
        max(dt * 9 * jh, dt * scale * writer_eh),
    )
    my = dt * (1 + scale * max(writer_emax, -writer_emin))
    v, vx, vh = hinv * causal, hinv * cx, hinv * ch + hinv**2 * causal
    ms, bx, bh = zeta * 5 * v * v, 10 * zeta * v * vx, 10 * zeta * v * vh
    ell = ax + ah * lip
    _require(0 <= theta < Q(1, 2) and ell < 1, "A current/base inverse not certified")
    inv = 1 / (1 - ell)
    value, image_lip = kh * ms, kh * (bx + bh * lip) * inv
    q = kh * (bh + (bx + bh * lip) * inv * ah)
    _require(
        advance < Q(1, 4)
        and my < Q(1, 8)
        and value < rho
        and image_lip <= lip
        and q < 1,
        "signed A section containment/self-map/contraction not certified",
    )
    bounds = {
        "base_X_lipschitz": ax,
        "base_h_lipschitz": ah,
        "base_displacement_upper": max(advance, my),
        "source_upper": ms,
        "source_X_lipschitz": bx,
        "source_h_lipschitz": bh,
        "inverse_lipschitz": inv,
        "contraction_upper": q,
        "section_lipschitz": lip,
        "section_radius": rho,
        "section_value_radius": value,
        "image_lipschitz": image_lip,
        "current_inverse_upper": 1 / (1 - theta),
        "current_upper": j,
        "resource_displacement_upper": advance,
        "scaled_log_displacement_upper": my,
    }
    return {
        "domain": domain,
        "selector_rank": 0,
        "graph_data": Algebra(
            b,
            gram,
            mask,
            tuple(tuple(tuple(r) for r in node) for node in rows),
            tuple(edge_ends),
        ),
        "bounds": FrozenJSONMap({k: str(v) for k, v in bounds.items()}),
    }


def _clip(v: Any, lo: int, hi: int) -> Any:
    v = _iv(v)
    return _Interval(max(Q(lo), min(Q(hi), v.lo)), max(Q(lo), min(Q(hi), v.hi)))


def literal(cert: Any, x: Any, h: Any) -> tuple[Any, Any, Any]:
    """Completed maps in exact C/Y coordinates, including the one W writer."""
    a = cert.graph_data
    n = len(a.incidence)
    c = tuple(_clip(v, -1, 5) for v in x[:n])
    y = tuple(_clip(v, -1, 1) for v in x[n:])
    w = tuple(_iexp(v / 512) for v in y)
    hi, bi, di = _im(h), _im(a.incidence), _im(a.gram)

    def exponent(cc: Any, jj: Any) -> tuple[Any, ...]:
        rows = []
        for i, node in enumerate(a.rows):
            rows.append(
                tuple(
                    sum((w[k] * (cc[v] - cc[i]) for k, v in row), _iv(0))
                    / sum((w[k] for k, _ in row), _iv(0))
                    if row
                    else _iv(0)
                    for row in node
                )
            )
        return tuple(
            Q(1, 2**25)
            * (
                cc[u]
                + cc[v]
                + sum(
                    ((r - s) * (r - s) for r, s in zip(rows[u], rows[v], strict=True)),
                    _iv(0),
                )
                + j * j
            )
            for (u, v), j in zip(a.ends, jj, strict=True)
        )

    b = _imm(tuple(zip(*bi, strict=True)), tuple((v,) for v in c))
    correction = _imm(
        tuple(
            tuple(v - int(i == k) for k, v in enumerate(row))
            for i, row in enumerate(hi)
        ),
        b,
    )
    phi = tuple(
        (ww * v[0] + Q(1, 2) * z[0],) for ww, v, z in zip(w, b, correction, strict=True)
    )
    j0 = tuple(-ww * r[0] for ww, r in zip(w, _imm(di, phi), strict=True))
    drive = tuple(_iexp(-v) for v in exponent(c, j0))
    q = tuple((ww - g) / (ww + g) for ww, g in zip(w, drive, strict=True))
    j = tuple(v / (_iv(1) - z / 32) for v, z in zip(j0, q, strict=True))
    flat = _imm(_iinverse(hi), tuple((z * v / 16,) for z, v in zip(q, j, strict=True)))
    image = tuple(
        tuple(
            _iv(int(i == k)) + Q(1, 4) * a.mask[i][k] * v[0] * z[0]
            for k, z in enumerate(flat)
        )
        for i, v in enumerate(flat)
    )
    dc = tuple(-Q(1, 4096) * r[0] for r in _imm(bi, tuple((v,) for v in j)))
    ew = exponent(tuple(v + d for v, d in zip(c, dc, strict=True)), j)
    decay = _iexp(_iv(-Q(1, 4096)))
    dy = tuple((1 - decay) * (-512 * e - v) for e, v in zip(ew, y, strict=True))
    return dc + dy, image, j


def propose(cert: Any, query: Any) -> tuple[Any, Any]:
    np = _dependency("numpy")
    a = cert.graph_data
    b, d, mask = (np.array(v, dtype=float) for v in (a.incidence, a.gram, a.mask))
    n, m = len(b), len(mask)
    ident = np.eye(m)
    x = [np.array(query, dtype=float) for _ in range(DEPTH + 1)]
    h = [ident.copy() for _ in range(DEPTH + 1)]

    def read(xi: Any, hi: Any) -> tuple[Any, Any]:
        c, y = np.clip(xi[:n], -1.0, 5.0), np.clip(xi[n:], -1.0, 1.0)
        w = np.array([math.exp(float(v) / 512) for v in y])

        def conductance(cc: Any, jj: Any) -> Any:
            rows = [
                [
                    sum(w[k] * (cc[v] - cc[i]) for k, v in row)
                    / sum(w[k] for k, _ in row)
                    if row
                    else 0.0
                    for row in node
                ]
                for i, node in enumerate(a.rows)
            ]
            return np.array(
                [
                    math.exp(
                        -(
                            cc[u]
                            + cc[v]
                            + sum(
                                (r - s) ** 2
                                for r, s in zip(rows[u], rows[v], strict=True)
                            )
                            + j * j
                        )
                        / 2**25
                    )
                    for (u, v), j in zip(a.ends, jj, strict=True)
                ]
            )

        dc0 = b.T @ c
        j0 = -w * (d @ (w * dc0 + 0.5 * ((hi - ident) @ dc0)))
        g = conductance(c, j0)
        q = (w - g) / (w + g)
        j = j0 / (1 - q / 32)
        flat = np.linalg.solve(hi, q * j / 16)
        dc = -(2**-12) * (b @ j)
        gw = conductance(c + dc, j)
        dy = np.array(
            [
                (1 - math.exp(-(2**-12))) * (512 * math.log(float(g)) - float(v))
                for g, v in zip(gw, y, strict=True)
            ]
        )
        return np.concatenate((dc, dy)), ident + 0.25 * mask * np.outer(flat, flat)

    for _ in range(SWEEPS):
        for i in range(1, DEPTH + 1):
            f, _ = read(x[i], h[i])
            x[i] = x[i - 1] - f
        for i in range(DEPTH, 0, -1):
            _, h[i - 1] = read(x[i], h[i])
    return x, h


def certify_chain(
    cert: Any, query: Any, x: Any, h: Any, exact_query: Any
) -> tuple[ExactScalar, dict[str, ExactScalar]]:
    """Validate recipe, operands and every residual; include finite-chain tail."""
    np = _dependency("numpy")
    a, domain = cert.graph_data, cert.domain
    n, m = len(a.incidence), len(a.gram)
    _require(len(x) == DEPTH + 1 and len(h) == DEPTH + 1, "wrong signed section depth")
    for values, shape in ((x, (n + m,)), (h, (m, m))):
        for v in values:
            _require(
                isinstance(v, np.ndarray)
                and v.dtype == np.dtype("float64")
                and v.shape == shape
                and bool(np.all(np.isfinite(v))),
                "invalid signed section operands",
            )
    _require(
        tuple(x[0]) == tuple(query) and bool(np.array_equal(h[-1], np.eye(m))),
        "section query or terminal identity changed",
    )
    for hi in h:
        _require(
            bool(np.array_equal(hi, hi.T))
            and all(a.mask[i][j] or hi[i, j] == 0 for i in range(m) for j in range(m))
            and infinity(
                tuple(
                    tuple(Q(float(hi[i, j])) - int(i == j) for j in range(m))
                    for i in range(m)
                )
            )
            <= Q(domain.h_radius),
            "signed section geometry symmetry/support/norm failure",
        )
    rx, rh = Q(), Q()
    for i in range(1, DEPTH + 1):
        f, g, _ = literal(cert, tuple(float(v) for v in x[i]), h[i].tolist())
        rx = max(
            rx,
            max(
                (_iv(float(v)) - float(w) + dv).magnitude
                for v, w, dv in zip(x[i], x[i - 1], f, strict=True)
            ),
        )
        rh = max(
            rh,
            infinity(
                tuple(
                    tuple(_iv(float(v)) - z for v, z in zip(row, other, strict=True))
                    for row, other in zip(h[i - 1], g, strict=True)
                )
            ),
        )
    b = {k: Q(v) for k, v in cert.bounds.items()}
    ax, ah, bx, bh = (
        b[k]
        for k in (
            "base_X_lipschitz",
            "base_h_lipschitz",
            "source_X_lipschitz",
            "source_h_lipschitz",
        )
    )
    amplification = sum(((1 - ax) ** (-i) for i in range(1, DEPTH + 1)), Q())
    denominator = 1 - Q(1, 2) * bh - Q(1, 2) * bx * amplification * ah
    _require(denominator > 0, "coupled chain error not certified")
    eh = (rh + Q(1, 2) * bx * amplification * rx) / denominator
    ex = amplification * (rx + ah * eh)
    tail = b["contraction_upper"] ** DEPTH * b["section_value_radius"]
    input_error = b["section_lipschitz"] * max(
        (_iv(float(v)) - z).magnitude for v, z in zip(x[0], exact_query, strict=True)
    )
    return eh + tail + input_error, {
        "input_error": input_error,
        "state_residual": rx,
        "geometry_residual": rh,
        "state_error": ex,
        "geometry_error": eh,
        "truncation_error": tail,
    }


def section(cert: Any) -> dict[str, Any]:
    inputs = cert.inputs
    exact_query = admit(inputs.current, ordinary=False)
    query = tuple(inputs.current.C) + tuple(
        512 * math.log(w) for w in inputs.current.W_A
    )
    params = inputs.geometry.reference.profile.params_resolved.realization
    evaluations = 2 * SWEEPS * DEPTH + DEPTH
    _require(
        params.iteration_limit >= evaluations,
        "RG2b deterministic evaluation budget exhausted",
    )
    try:
        x, h = propose(cert, tuple(query))
    except (ArithmeticError, ValueError) as exc:
        raise RG2bStageError("signed A section proposal failed") from exc
    error, _ = certify_chain(cert, tuple(query), x, h, exact_query)
    _require(
        error <= Q(params.error_tolerance),
        "signed A section error tolerance unresolved",
    )
    geometry = GRCV4Geometry(
        inputs.geometry.reference,
        OneFormHodge(inputs.geometry.reference.graph, tuple(map(tuple, h[0].tolist()))),
    )
    from .grc_v4_rg2b_graph import rounded_upper

    return {
        "geometry": geometry,
        "enclosure": (str(-rounded_upper(error)), str(rounded_upper(error))),
        "error_upper": str(rounded_upper(error)),
        "levels": DEPTH,
        "evaluations": evaluations,
    }


def native_bridge(
    section: Any, point: Any, following: Any, generated: Any
) -> tuple[Any, ...]:
    x = coordinates(section.inputs.current)
    f, g, j = literal(section.certificate, x, section.geometry.one_form_hodge.matrix)
    y = coordinates(following.current)
    je = _norm(
        (_iv(v) - z).magnitude for v, z in zip(point.current.values, j, strict=True)
    )
    # This is an error in (C,512 log W), never a raw W-space discrepancy.
    xe = max((v - old - delta).magnitude for v, old, delta in zip(y, x, f, strict=True))
    he = infinity(
        tuple(
            tuple(_iv(v) - z for v, z in zip(row, other, strict=True))
            for row, other in zip(generated.one_form_hodge.matrix, g, strict=True)
        )
    )
    return je, xe, he, _norm(z.magnitude for z in j)
