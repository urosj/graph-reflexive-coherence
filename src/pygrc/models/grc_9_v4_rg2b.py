"""Native C_RG2b signed argument completion and certified finite section.

The six-level coupled chain is numerical work, never state or a CI root.
ExactScalar/160-bit outward intervals certify every returned coordinate and
the tail to the unique completion-relative Lipschitz section. Physical C is
never clipped. The separately identified auxiliary domain includes signed C.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from . import grc_v4_numerics as numerics
from .grc_v4_candidate_c import CandidateCCurrent, _c_components
from .grc_v4_ci import _iexp, _iinverse, _im, _imm, _itanh, _iv, _norm
from .grc_v4_codec import _dependency
from .grc_v4_exact import ExactScalar
from .grc_v4_exact import exact_number as Q
from .grc_v4_geometry import GRCV4Geometry, OneFormHodge
from .grc_v4_rg2b import RG2bDomain, RG2bStageError, _require
from .grc_v4_state import FrozenJSONMap

EXTENSION = "grc9v4_c_rg2b_signed_argument_completion_v1"
APPROXIMATION = "grc9v4_c_rg2b_chain6_sweeps18_binary64_interval160_v1"
ERROR_NORM = "grc9v4_rg2b_hodge_induced_infinity_v1"
CONTAINMENT = "grc9v4_c_rg2b_signed_tree17_global_certificate_v1"
DEPTH, SWEEPS = 6, 18


@dataclass(frozen=True, slots=True)
class NativeCRG2bDomain(RG2bDomain):
    """K_minus=[-1/4,17/4], K=[-1/2,9/2], auxiliary clamp=[-1,5]."""

    def __post_init__(self) -> None:
        expected = (2.0, 1.0, 2.25, 2.5, 3.0, 2**-12, 2**-10, 2**-12)
        _require(
            tuple(getattr(self, k) for k in self.__dataclass_fields__) == expected
            and all(type(getattr(self, k)) is float for k in self.__dataclass_fields__),
            "native C_RG2b requires its exact signed completion coordinates",
        )

    @property
    def identity(self) -> str:
        return EXTENSION

    @classmethod
    def from_identity(cls, value: object) -> NativeCRG2bDomain:
        _require(type(value) is str and value == EXTENSION, "unknown signed completion")
        return cls(2.0, 1.0, 2.25, 2.5, 3.0, 2**-12, 2**-10, 2**-12)


def infinity(matrix: Any) -> ExactScalar:
    return max(
        (sum((_iv(v).magnitude for v in row), Q()) for row in matrix), default=Q()
    )


@dataclass(frozen=True, slots=True)
class Algebra:
    incidence: Any
    gram: Any
    mask: Any


def certificate(inputs: Any, backend: Any, domain: NativeCRG2bDomain) -> dict[str, Any]:
    """Uniform graph/parameter hypotheses, then exact global Banach bounds.

    The mask is the actual normalized vertex-star assembly (diagonal 1,
    shared-vertex off-diagonal 1/2). No commuting H/D assumption is used.
    """
    ref = inputs.geometry.reference
    graph, p = ref.graph, ref.profile.params_resolved.candidate
    n, m = len(graph.live_node_ids), len(graph.live_edge_ids)
    _require(
        backend is None and graph.port_graph is not None, "native C port owner required"
    )
    _require(ref.profile.identity_payload.profile_family_id == "C_RG2b", "C_RG2b only")
    _require(
        2 <= n <= 17
        and m == n - 1
        and len(_c_components(graph)) == 1
        and all(e.tail_node_id != e.head_node_id for e in graph.oriented_edges),
        "signed completion requires a connected tree with at most 17 vertices",
    )
    _require(
        all(
            getattr(p, name) == value
            for name, value in {
                "Lambda_C": 2**-9,
                "C_ref": 1,
                "kappa_M_C": 2**-24,
                "kappa_Phi_C": 1,
                "eta_C": 1,
                "tau_C": 1,
                "chi_C": 16,
                "zeta_C": 2**-37,
            }.items()
        )
        and ref.profile.params_resolved.geometry.kappa_H == 0.5
        and all(v == 1 for v in ref.edge_weights.values())
        and all(v == 0 for row in ref.K4_base for v in row),
        "signed completion parameter/reference binding mismatch",
    )
    b = numerics.exact_matrix(graph.incidence)
    gram = numerics.matmul(numerics.transpose(b), b)
    ends = [{e.tail_node_id, e.head_node_id} for e in graph.oriented_edges]
    mask = tuple(tuple(Q(len(u & v), 2) for v in ends) for u in ends)
    _require(
        infinity(b) <= 9 and infinity(gram) <= 10 and infinity(mask) <= 5,
        "signed completion graph norm hypotheses fail",
    )
    rho, lip, dt, kh = Q(1, 4096), Q(1, 1024), Q(1, 4096), Q(1, 2)
    _require(
        (1 - rho) / (n * (n - 1)) > Q(p.Lambda_C), "constant selector not certified"
    )
    _require(
        (1 + rho) / (1 - rho)
        <= Q(ref.profile.params_resolved.solver.conditioning_limit),
        "signed Hodge ball conditioning not certified",
    )
    # Also admit the full native candidate policies and exact selector at reference.
    CandidateCCurrent(inputs)
    chi, zeta, km = Q(16), Q(1, 2**37), Q(1, 2**24)
    t, hinv = 1 / (1 - km), 1 / (1 - rho)
    tx, r = t * km, 4 * (1 + rho) / (1 - rho)
    theta = chi * zeta * r
    j0, j0x, j0h = t * 10 * (1 + rho) * 6, 10 * (1 + rho) * (2 * t + 6 * tx), t * 60
    rx, rh = r * r * tx * (1 + rho) * 10, r * r * t * 10
    j = j0 / (1 - theta)
    jx, jh = (
        (j0x + chi * zeta * rx * j) / (1 - theta),
        (j0h + chi * zeta * rh * j) / (1 - theta),
    )
    causal = chi * r * (1 + 20 * t * rho) * 6 / (1 - theta)
    cx, ch = chi * (rx * j + r * jx), chi * (rh * j + r * jh)
    v, vx, vh = hinv * causal, hinv * cx, hinv * ch + hinv * hinv * causal
    ax, ah, mf = dt * 9 * jx, dt * 9 * jh, dt * 9 * j
    ms, bx, bh = zeta * 5 * v * v, 10 * zeta * v * vx, 10 * zeta * v * vh
    ell = ax + ah * lip
    _require(0 <= theta < Q(1, 2) and ell < 1, "current/base inverse not certified")
    inv = 1 / (1 - ell)
    value, image_lip = kh * ms, kh * (bx + bh * lip) * inv
    q = kh * (bh + (bx + bh * lip) * inv * ah)
    _require(
        mf < Q(1, 4) and value < rho and image_lip <= lip and q < 1,
        "signed section containment/self-map/contraction not certified",
    )
    bounds = {
        "base_X_lipschitz": ax,
        "base_h_lipschitz": ah,
        "base_displacement_upper": mf,
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
    }
    return {
        "domain": domain,
        "selector_rank": 1,
        "graph_data": Algebra(b, gram, mask),
        "bounds": FrozenJSONMap({k: str(v) for k, v in bounds.items()}),
    }


def literal(cert: Any, x: Any, h: Any) -> tuple[Any, Any, Any]:
    """Real completed C maps at exact represented operands, enclosed outward.

    Solving (I+tHD-pI)u=J0 gives RJ=u and J=J0+pu. This retains
    noncommuting DH in J0 and HD in the resolvent. Only arguments are clamped.
    """
    a = cert.graph_data
    c = tuple((_iv(min(Q(5), max(Q(-1), Q(v)))),) for v in x)
    hi, bi, di = _im(h), _im(a.incidence), _im(a.gram)
    bt = tuple(zip(*bi, strict=True))
    t = _iexp(Q(1, 2**24) * _itanh(sum((r[0] for r in c), _iv(0)) / len(c)))
    b = _imm(bt, c)
    j0 = tuple((-t * row[0],) for row in _imm(di, _imm(hi, b)))
    hd = _imm(hi, di)
    p = Q(1, 2**33)
    matrix = tuple(
        tuple(_iv(int(i == k) * (1 - p)) + t * v for k, v in enumerate(row))
        for i, row in enumerate(hd)
    )
    u = _imm(_iinverse(matrix), j0)
    j = tuple((v[0] + p * w[0],) for v, w in zip(j0, u, strict=True))
    flat = _imm(_iinverse(hi), tuple((16 * r[0],) for r in u))
    source = tuple(
        tuple(Q(1, 2**37) * a.mask[i][k] * v[0] * w[0] for k, w in enumerate(flat))
        for i, v in enumerate(flat)
    )
    f = tuple(-Q(1, 4096) * row[0] for row in _imm(bi, j))
    image = tuple(
        tuple(_iv(int(i == k)) + Q(1, 2) * v for k, v in enumerate(row))
        for i, row in enumerate(source)
    )
    return f, image, tuple(row[0] for row in j)


def propose(cert: Any, query: Any) -> tuple[Any, Any]:
    """Fixed binary64 work recipe; convergence is decided only by recertification."""
    np = _dependency("numpy")
    a = cert.graph_data
    b, d, mask = (np.array(v, dtype=float) for v in (a.incidence, a.gram, a.mask))
    ident = np.eye(len(mask))
    x = [np.array(query, dtype=float) for _ in range(DEPTH + 1)]
    h = [ident.copy() for _ in range(DEPTH + 1)]

    def read(xi: Any, hi: Any) -> tuple[Any, Any]:
        c = np.clip(xi, -1.0, 5.0)
        t = math.exp(2**-24 * math.tanh(math.fsum(c) / len(c)))
        j0 = -t * (d @ (hi @ (b.T @ c)))
        u = np.linalg.solve(ident + t * (hi @ d) - 2**-33 * ident, j0)
        j = j0 + 2**-33 * u
        flat = np.linalg.solve(hi, 16 * u)
        return -(2**-12) * (b @ j), ident + 2**-38 * mask * np.outer(flat, flat)

    for _ in range(SWEEPS):
        for i in range(1, DEPTH + 1):
            f, _ = read(x[i], h[i])
            x[i] = x[i - 1] - f
        for i in range(DEPTH, 0, -1):
            _, h[i - 1] = read(x[i], h[i])
    return x, h


def certify_chain(
    cert: Any, query: Any, x: Any, h: Any
) -> tuple[ExactScalar, dict[str, ExactScalar]]:
    """Validate recipe, operands and every residual; include finite-chain tail."""
    np = _dependency("numpy")
    a, domain = cert.graph_data, cert.domain
    n, m = len(a.incidence), len(a.gram)
    _require(len(x) == DEPTH + 1 and len(h) == DEPTH + 1, "wrong signed section depth")
    for values, shape in ((x, (n,)), (h, (m, m))):
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
    return eh + tail, {
        "state_residual": rx,
        "geometry_residual": rh,
        "state_error": ex,
        "geometry_error": eh,
        "truncation_error": tail,
    }


def section(cert: Any) -> dict[str, Any]:
    inputs, d = cert.inputs, cert.domain
    query = inputs.current.C
    _require(
        all(abs(Q(v) - 2) <= Q(d.core) for v in query),
        "RG2b section query is outside K",
    )
    params = inputs.geometry.reference.profile.params_resolved.realization
    evaluations = 2 * SWEEPS * DEPTH + DEPTH
    _require(
        params.iteration_limit >= evaluations,
        "RG2b deterministic evaluation budget exhausted",
    )
    # Copies isolate certificate operands from producer scratch ownership.
    try:
        x, h = propose(cert, tuple(query))
    except (ArithmeticError, ValueError) as exc:
        raise RG2bStageError("signed section proposal failed") from exc
    error, _ = certify_chain(cert, tuple(query), x, h)
    _require(
        error <= Q(params.error_tolerance), "signed section error tolerance unresolved"
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
    f, g, j = literal(
        section.certificate,
        section.inputs.current.C,
        section.geometry.one_form_hodge.matrix,
    )
    # Current error follows the common edge_l2 solver convention. Resource
    # and Hodge errors use the signed completion's induced infinity norms.
    je = _norm(
        (_iv(v) - z).magnitude for v, z in zip(point.current.values, j, strict=True)
    )
    xe = max(
        (_iv(v) - old - delta).magnitude
        for v, old, delta in zip(
            following.current.C, section.inputs.current.C, f, strict=True
        )
    )
    he = infinity(
        tuple(
            tuple(_iv(v) - z for v, z in zip(row, other, strict=True))
            for row, other in zip(generated.one_form_hodge.matrix, g, strict=True)
        )
    )
    return je, xe, he, _norm(z.magnitude for z in j)
