"""Full continuous C_RG2b charge-domain proof; no section derivative or tail orbit.

Every coefficient, metric, spatial inequality, inverse footprint and self-map
margin is recomputed from the graph-bound exact operands. Research verdicts and
trajectories are neither inputs nor numerical oracles.
"""

import itertools
from functools import lru_cache
from math import comb

from flint import arb, arb_mat, ctx, fmpq, fmpq_mat

from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_spark_cos import _matrix
from .grc_v4_spark_crg2b_math import (
    DT,
    ETA,
    LIP,
    F,
    ball,
    exact_bounds,
    maxnorm,
    need,
    norm_upper,
)
from .grc_v4_spark_state import ExactResources, flint_operation, rational
from .grc_v4_state import FrozenJSONMap

QUERY_RADIUS = F(7, 50)
INVERSE_RADIUS = F(1, 5)


def positive_definite_exact(M):
    need(
        M.nrows() == M.ncols() and M == M.transpose(),
        "symmetric exact metric comparison required",
    )
    M = fmpq_mat(M)
    pivots = []
    for k in range(M.nrows()):
        pivot = M[k, k]
        need(pivot > 0, "exact charge-tangent LDL not positive")
        pivots.append(str(pivot))
        for i in range(k + 1, M.nrows()):
            for j in range(k + 1, M.ncols()):
                M[i, j] -= M[i, k] * M[k, j] / pivot
    return pivots


def cheb_product(a, b):
    out = [fmpq(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y / 2
            out[abs(i - j)] += x * y / 2
    return out


def cheb_times_x(a):
    out = [fmpq(0)] * (len(a) + 1)
    for i, x in enumerate(a):
        out[i + 1] += x / 2
        out[abs(i - 1)] += x / 2
    return out


def curve_at(Q, s):
    """Exact rational evaluation, including charge, at a rational parameter."""
    x = 2 * fmpq(str(s)) - 1
    t = [fmpq(1), x]
    for _ in range(2, Q.ncols()):
        t.append(2 * x * t[-1] - t[-2])
    return Q * fmpq_mat([[v] for v in t[: Q.ncols()]])


def reference_residual(m, Q, rho):
    """Uniform P norm via the sum of exact Chebyshev coefficient norms."""
    d = Q.ncols() - 1
    composition = [[fmpq(1)], [rho - 1, rho]]
    for _ in range(1, d):
        old = composition[-1]
        new = cheb_times_x(old)
        for j in range(len(new)):
            new[j] = (
                2 * rho * new[j]
                + (2 * (rho - 1) * old[j] if j < len(old) else 0)
                - (composition[-2][j] if j < len(composition[-2]) else 0)
            )
        composition.append(new)
    K = fmpq_mat(
        [
            [composition[i][j] if j < len(composition[i]) else 0 for j in range(d + 1)]
            for i in range(d + 1)
        ]
    )
    h = fmpq(str(ETA * DT))
    A = m.algebra["A"]
    L = m.algebra["L"]
    linear = Q + h * A * L * Q / 64 - Q * K
    site = []
    for i in range(m.n):
        a = [Q[i, k] for k in range(d + 1)]
        a[0] -= 2
        cubic = cheb_product(cheb_product(a, a), a)
        for k, z in enumerate(a):
            cubic[k] -= z
        site.append(cubic)
    residual = -h * A * fmpq_mat(site)
    for i in range(m.n):
        for k in range(d + 1):
            residual[i, k] += linear[i, k]
    bound = arb(0)
    for k in range(residual.ncols()):
        v = fmpq_mat([[residual[i, k]] for i in range(m.n)])
        need(sum(v.entries()) == 0, "functional residual leaves exact charge tangent")
        squared = (v.transpose() * m.algebra["P"] * v)[0, 0]
        need(squared >= 0, "negative exact metric square")
        bound += arb(squared).sqrt()
    return bound.upper(), residual


def split_bernstein(row):
    row = list(row)
    left = [row[0]]
    right = [row[-1]]
    while len(row) > 1:
        row = [(a + b) / 2 for a, b in itertools.pairwise(row)]
        left.append(row[0])
        right.append(row[-1])
    return left, right[::-1]


def bernstein_cells(Q, depth):
    d = Q.ncols() - 1
    powers = [[1], [-1, 2]]
    for _ in range(1, d):
        old = powers[-1]
        new = [0] * (len(old) + 1)
        for j, z in enumerate(old):
            new[j] -= 2 * z
            new[j + 1] += 4 * z
        for j, z in enumerate(powers[-2]):
            new[j] -= z
        powers.append(new)
    T = fmpq_mat(
        [
            [powers[k][j] if j < len(powers[k]) else 0 for j in range(d + 1)]
            for k in range(d + 1)
        ]
    )
    B = fmpq_mat(
        [
            [fmpq(comb(i, j), comb(d, j)) if i >= j else 0 for i in range(d + 1)]
            for j in range(d + 1)
        ]
    )
    cells = [(Q * T * B).tolist()]
    for _ in range(depth):
        new = []
        for cell in cells:
            halves = [split_bernstein(row) for row in cell]
            new.extend(([x[0] for x in halves], [x[1] for x in halves]))
        cells = new
    return cells


class CurveBounds:
    """Exact Bernstein linear forms plus exact charge-tangent dual norm.

    For arbitrary w, sup_{1^T v=0, ||v||_P<=R} |w^T v| =
    R sqrt(w^T A w).  Correlation matters for small edge differences.
    """

    def __init__(self, m, Q, radius, depth):
        self.m = m
        self.cells = bernstein_cells(Q, depth)
        self.radius = ball(radius)
        self.cache = {}

    def linear(self, weights):
        key = tuple(map(str, weights))
        if key in self.cache:
            return self.cache[key]
        w = [fmpq(str(x)) for x in weights]
        terms = [(i, x) for i, x in enumerate(w) if x]
        values = [
            sum(x * cell[i][k] for i, x in terms)
            for cell in self.cells
            for k in range(len(cell[0]))
        ]
        vector = fmpq_mat([w])
        sq = (vector * self.m.algebra["A"] * vector.transpose())[0, 0]
        need(sq >= 0, "negative dual metric square")
        width = self.radius * arb(sq).sqrt()
        result = (
            (arb(min(values)) - width).lower(),
            (arb(max(values)) + width).upper(),
        )
        self.cache[key] = result
        return result

    def coordinate(self, i):
        return self.linear([int(j == i) for j in range(self.m.n)])

    def difference(self, i, j):
        return self.linear([int(k == i) - int(k == j) for k in range(self.m.n)])

    def box(self):
        ranges = [self.coordinate(i) for i in range(self.m.n)]
        return arb_mat(
            [
                [arb((a.fmpq() + b.fmpq()) / 2, (b.fmpq() - a.fmpq()) / 2)]
                for a, b in ranges
            ]
        )


def local_section(m, center, box):
    """Local inverse cube and section differences, using only global Lip(Gamma).

    The inverse cube is independently closed by Banach iteration.  Global inverse
    uniqueness identifies it with the frozen completion inverse.  Thus local G
    partial bounds imply local section value/Lipschitz bounds without D Gamma.
    """
    C = m.vector(center)
    a = m.algebra
    s0 = m.enclose(C)
    w = max(abs(box[i, 0] - C[i, 0]).upper() for i in range(m.n))
    need(w < ball(QUERY_RADIUS), "query cube does not contain curve hull")
    R = ball(INVERSE_RADIUS)
    V = m.bounds["section_value_radius"]
    ell = ball(a["ell"])
    b = ball(a["b"])
    ss = ball(a["s"])
    a0 = ball(a["a0"])
    need(a0 * V * ell < 1 and V < 1, "local resolvent premises")
    inverse = a0 / (1 - a0 * V * ell)
    hinv = 1 / (1 - V)
    M = arb_mat(a["M"])
    MD = M * m.Le
    cb = arb_mat([[arb(z.fmpq(), fmpq(str(INVERSE_RADIUS)))] for z in C.entries()])
    need(
        all(ball(m.lo) < x < ball(m.hi) for x in cb.entries()),
        "inverse footprint crosses argument retraction",
    )
    curv = arb_mat(
        [
            [3 * (cb[i, 0] - 2) ** 2 - 1 if i == j else 0 for j in range(m.n)]
            for i in range(m.n)
        ]
    )
    D = arb_mat(a["L"]) / 64 - curv
    h = ball(ETA * DT)
    reference = maxnorm(h * m.A * D)
    dmax = max(abs(curv[i, i]).upper() for i in range(m.n))
    qdiff = inverse * V * ell * a0 / 4
    perturb = (
        h * b * 2 * (qdiff * (dmax + 2 * b / 64) + (1 + inverse / 4) * 2 * b * V / 64)
    )
    ell_local = reference + perturb + m.bounds["A_H"] * ball(LIP)
    f0 = maxnorm(s0["read"]["increment"])
    inverse_margin = R - ball(QUERY_RADIUS) - f0 - ell_local * R
    need(
        ell_local < 1 and inverse_margin > 0,
        "local inverse cube not a strict contraction/self-map",
    )
    inverse_lip = 1 / (1 - ell_local)
    YX0 = maxnorm(-ball(ETA) * M * m.Bt * D)
    read0 = m.lag(C, m.operators(m.I))
    Y0 = maxnorm(read0["causal_flat"] * 2)
    z = maxnorm(m.Bt * cb)
    eps = a0 * V * ell
    Y = (Y0 + YX0 * R + ball(ETA) * maxnorm(MD) * V * z / 64) / (1 - eps)
    YX = (YX0 + ball(ETA) * maxnorm(MD) * V * 2 / 64) / (1 - eps)
    j0x = maxnorm(-ball(ETA) * m.Bt * D)
    j0 = maxnorm(read0["baseline"]) + j0x * R + ball(ETA) * ell * V * z / 64
    DY = min(ell * Y, hinv * (j0 + 3 * Y / 4))
    YH = inverse * (ball(ETA) * ell * z / 64 + DY)
    flat = hinv * Y / 2
    flatX = hinv * YX / 2
    flatH = hinv * (YH / 2 + flat)
    GX = 2 * ss * flat * flatX
    GH = 2 * ss * flat * flatH
    lip = ((GX + GH * ball(LIP)) * inverse_lip).upper()
    value = (ss * flat**2).upper()
    need(
        0 < lip < ball(LIP) and 0 < value < V,
        "local section bounds do not improve global ones",
    )
    record = {
        "query_cube_radius": str(QUERY_RADIUS),
        "inverse_cube_radius": str(INVERSE_RADIUS),
        "hull_width": exact_bounds(w),
        "inverse_cube_margin": exact_bounds(inverse_margin),
        "inverse_increment_lipschitz": exact_bounds(ell_local),
        "inverse_lipschitz": exact_bounds(inverse_lip),
        "geometry_X": exact_bounds(GX),
        "geometry_H": exact_bounds(GH),
        "current_value": exact_bounds(Y),
        "current_X": exact_bounds(YX),
        "current_H": exact_bounds(YH),
        "section_lipschitz": exact_bounds(lip),
        "section_value_radius": exact_bounds(value),
        "global_section_lipschitz_used": str(LIP),
        "global_section_value_radius": exact_bounds(V),
        "section_C1_claimed": False,
        "inverse_is_frozen_completion_inverse": True,
    }
    return lip, value, record


def physical_bounds(m, box, lip, value):
    """Common full-state difference bound and absolute F-Gamma versus F-I error."""
    n = m.n
    curv = [3 * (x - 2) ** 2 - 1 for x in box.entries()]
    low = (
        fmpq_mat(
            [
                [curv[i].lower().fmpq() if i == j else 0 for j in range(n)]
                for i in range(n)
            ]
        )
        - m.algebra["L"] / 64
    )
    high = (
        fmpq_mat(
            [
                [curv[i].upper().fmpq() if i == j else 0 for j in range(n)]
                for i in range(n)
            ]
        )
        - m.algebra["L"] / 64
    )
    E = fmpq_mat(
        [[int(i == j) if i < n - 1 else -1 for j in range(n - 1)] for i in range(n)]
    )
    P = m.algebra["P"]
    pl = positive_definite_exact(E.transpose() * (low - P / 3) * E)
    ph = positive_definite_exact(E.transpose() * (64 * P - high) * E)
    ell = ball(m.algebra["ell"])
    h = ball(ETA * DT)
    V = value
    a2 = (1 + V) / (1 - V) * m.q(4, 3)
    q2 = 1 + a2 / 4
    D0 = max(abs(x).upper() for x in curv) + ell / 64
    partial = h * ell * (a2 * V * ell / 3 * D0 + q2 * ell * V / 64)
    z = norm_upper(m.Bt * box)
    phi = m.B * m.Bt * box / 64 - m.site(box)
    j0 = ball(ETA) * norm_upper(m.Bt * phi) + ball(ETA) * ell * V * z / 64
    y = a2 * j0
    hslope = ball(DT) * ell.sqrt() * (ball(ETA) * ell * z * q2 / 64 + a2 * ell * y / 4)
    convert = (m.amax * m.trace).sqrt()
    reference = max(abs(1 - h / 3), abs(1 - 64 * h))
    fixed = partial * convert
    section = hslope * lip * convert
    q = (reference + fixed + section).upper()
    error = (m.trace.sqrt() * hslope * V).upper()
    need(
        0 < fixed and 0 < section and 0 < error and q < 1,
        "full physical curve contraction fails",
    )
    return (
        q,
        error,
        {
            "contraction": exact_bounds(q),
            "reference_contraction": exact_bounds(reference),
            "fixed_geometry_correction": exact_bounds(fixed),
            "section_difference_correction": exact_bounds(section),
            "geometry_value_correction": exact_bounds(error),
            "H_slope": exact_bounds(hslope),
            "charge_tangent_rayleigh_bounds": ["1/3", "64"],
            "exact_ldl_pivots": {"lower": pl, "upper": ph},
            "relative_dimension": n - 1,
            "all_independent_coordinates": True,
            "both_H_consumers": True,
            "section_C1_claimed": False,
        },
    )


def geometry(kernel, policy, bounds, center):
    from .grc_9_v4_completion import classify, terminal_roster

    nodes = kernel.graph.live_node_ids
    len(nodes)
    index = {x: i for i, x in enumerate(nodes)}
    down = {x: set() for x in nodes}
    adjacent = {x: set() for x in nodes}
    terms = {x: [[], [], []] for x in nodes}
    for e in kernel.graph.port_graph.edges:
        a, b = e.tail.node_id, e.head.node_id
        i, j = index[a], index[b]
        low, high = bounds.difference(j, i)
        low, high = (low, high) if policy.landscape_sign == 1 else (-high, -low)
        need(low > 0 or high < 0, "curved domain crosses edge order")
        down[b if low > 0 else a].add(a if low > 0 else b)
        adjacent[a].add(b)
        adjacent[b].add(a)
        for here, there in ((e.tail, e.head), (e.head, e.tail)):
            terms[here.node_id][(here.port - 1) // 3].append(there.node_id)
    g, h, contrast, resource = map(
        ball,
        (
            policy.epsilon_gradient,
            policy.epsilon_Hessian,
            policy.contrast,
            policy.minimum_resource,
        ),
    )
    seeds = set()
    anchors = set()
    row_bounds = {}
    for x in nodes:
        rows = []
        for neighbors in terms[x]:
            w = [
                F(neighbors.count(v), len(neighbors)) - int(v == x)
                if neighbors
                else F(0)
                for v in nodes
            ]
            low, high = bounds.linear(w)
            rows.append((low, high) if policy.landscape_sign == 1 else (-high, -low))
        row_bounds[x] = [[str(a.fmpq()), str(b.fmpq())] for a, b in rows]
        upper = sum(max(abs(a), abs(b)) ** 2 for a, b in rows)
        lower = sum(
            arb(0) if a <= 0 <= b else min(abs(a), abs(b)) ** 2 for a, b in rows
        )
        seed = upper < g * g and min(a for a, _ in rows) > h
        need(
            seed or lower >= g * g or min(b for _, b in rows) <= h,
            "whole-curve seed predicate unresolved",
        )
        if not seed:
            continue
        seeds.add(x)
        lo, hi = bounds.coordinate(index[x])
        gaps = []
        for y in adjacent[x]:
            a, b = bounds.difference(index[y], index[x])
            gaps.append((a, b) if policy.landscape_sign == 1 else (-b, -a))
        anchor = bool(gaps) and lo > resource and all(a > contrast for a, _ in gaps)
        need(
            anchor or not gaps or hi <= resource or any(b <= contrast for _, b in gaps),
            "whole-curve anchor predicate unresolved",
        )
        if anchor:
            anchors.add(x)
    roster, terminals = terminal_roster(nodes, down, anchors)
    point = classify(center, policy)
    need(
        (roster, terminals) == (point.basins, point.terminals),
        "center and full curve roster disagree",
    )
    return {
        "classification": point.to_payload(),
        "row_bounds": row_bounds,
        "seeds": [x for x in nodes if x in seeds],
        "all_parameters_certified_continuously": True,
        "bernstein_cells": len(bounds.cells),
    }


def verify(data):
    from .grc_9_v4_completion_certificate import binding
    from .grc_9_v4_completion_codec import CompletionPolicy, digest
    from .grc_v4_geometry import GRCV4Graph
    from .grc_v4_spark import quartic_kernel, quartic_profile

    expected = {
        "schema_version",
        "binding",
        "center",
        "curve",
        "radius",
        "parameter_decay",
        "subdivision_depth",
    }
    need(
        set(data) == expected
        and data["schema_version"] == "grc9v4-native-crg2b-curve-operands-v1",
        "closed full curved domain operands required",
    )
    b = data["binding"]
    k = quartic_kernel(
        GRCV4Graph.from_payload(b["graph"]), quartic_profile(b["profile"])
    )
    policy = CompletionPolicy.from_payload(b["policy"])
    need(
        k.profile.FAMILY == "C_RG2b"
        and policy.numerical_policy_id == k.profile.NUMERICS
        and policy.step_duration == "8"
        and b == binding(k, policy, b["role"], b["charge"]),
        "C_RG2b full equation/role/duration binding",
    )
    Q = _matrix(data["curve"])
    n = len(k.graph.live_node_ids)
    R = rational(data["radius"])
    rho = rational(data["parameter_decay"])
    need(
        (Q.nrows(), Q.ncols()) == (n, 41)
        and n == 15
        and R == F(1, 4096)
        and rho == F(999, 1000)
        and data["subdivision_depth"] == 6,
        "declared direct full-dimensional curve required",
    )
    need(
        all(
            sum(Q[i, j] for i in range(n)) == (rational(b["charge"]) if j == 0 else 0)
            for j in range(Q.ncols())
        ),
        "exact curve charge identity",
    )
    center = ExactResources(k.graph, tuple(data["center"]), b["charge"])
    need(
        curve_at(Q, 0) == fmpq_mat([[rational(x)] for x in center.C]),
        "curve origin mismatch",
    )
    with _ARB_CONTEXT_LOCK, ctx.workprec(k.precision_bits):
        m = k.section_math()
        bounds = CurveBounds(m, Q, R, 6)
        box = bounds.box()
        km = list(map(ball, m.domain["K_minus"]))
        need(
            all(0 < x and km[0] < x < km[1] for x in box.entries()),
            "whole curve leaves positive physical domain",
        )
        geometric = geometry(k, policy, bounds, center)
        reference, residual = reference_residual(m, Q, rho)
        lip, value, local = local_section(
            m, dict(zip(m.nodes, center.C, strict=True)), box
        )
        q, correction, physical = physical_bounds(m, box, lip, value)
        defect = (reference + correction).upper()
        margin = ((1 - q) * ball(R) - defect).lower()
        need(q < 1 and margin > 0, "continuous domain self-map not strict")
        numeric = k.uniform_metric_error(str(margin.fmpq()))
        return FrozenJSONMap(
            {
                "q": str(q.fmpq()),
                "image_margin": str(margin.fmpq()),
                "full_step_error": numeric,
                "represented_image_margin": str(
                    (margin - ball(numeric)).lower().fmpq()
                ),
                "center_defect": str(defect.fmpq()),
                "reference_functional_defect": exact_bounds(reference),
                "residual_degree": residual.ncols() - 1,
                "local_section": local,
                "physical_difference_bound": physical,
                "geometry": geometric,
                "relative_dimension": n - 1,
                "full_physical_state": ["C"],
                "all_parameters_certified_continuously": True,
                "section_C1_claimed": False,
                "future_trajectory_required": False,
                "supporting_trajectory_steps_after_completion": 0,
                "precision_bits": k.precision_bits,
                "metric": "charge_tangent_P=(A+11T/n)^-1",
                "operands_digest": digest(data),
            }
        )


@lru_cache(maxsize=16)
def _curve_grid(rows):
    Q = _matrix(rows)
    return tuple(
        tuple(str(x) for x in curve_at(Q, F(i, 64)).entries()) for i in range(65)
    )


def curve_derivatives(Q, s):
    x = 2 * s - 1
    t = [F(1), x]
    d = [F(0), F(2)]
    dd = [F(0), F(0)]
    for i in range(2, Q.ncols()):
        t.append(2 * x * t[-1] - t[-2])
        d.append(4 * t[i - 1] + 2 * x * d[-1] - d[-2])
        dd.append(8 * d[i - 1] + 2 * x * dd[-1] - dd[-2])
    return tuple(Q * fmpq_mat([[v] for v in values]) for values in (t, d, dd))


@flint_operation
def membership_details(certificate, state):
    b = certificate.operands["binding"]
    need(
        type(state) is ExactResources
        and state.graph.to_payload() == b["graph"].to_dict()
        and state.charge == b["charge"],
        "curve membership graph/charge binding",
    )
    from .grc_v4_codec import canonical_json_bytes
    from .grc_v4_spark_crg2b_math import graph_algebra

    Q = _matrix(certificate.operands["curve"])
    P = graph_algebra(canonical_json_bytes(state.graph.to_payload()).decode())["P"]
    C = fmpq_mat([[rational(x)] for x in state.C])
    R = rational(certificate.operands["radius"])

    def distance(s, values=None):
        point = (
            curve_at(Q, s)
            if values is None
            else fmpq_mat([[rational(x)] for x in values])
        )
        delta = C - point
        return (delta.transpose() * P * delta)[0, 0]

    endpoints = [(distance(s), s) for s in (F(0), F(1))]
    best = min(endpoints)
    if best[0] <= R * R:
        return {
            "inside": True,
            "parameter": str(best[1]),
            "squared_norm": str(best[0] / (R * R)),
            "method": "exact_rational_curve_witness; nonadmission_is_conservative",
        }
    grid = _curve_grid(tuple(tuple(row) for row in certificate.operands["curve"]))
    best = min((distance(F(i, 64), values), F(i, 64)) for i, values in enumerate(grid))
    s = best[1]
    scale = 2**32
    candidates = {F(0), F(1), s}
    # A grid supplies proposals only. The exact P inequality alone admits;
    # no assumption of convexity or uniqueness of the closest parameter is used.
    for _ in range(12):
        s = F((s.numerator * scale) // s.denominator, scale)
        candidates.add(s)
        p, d, dd = curve_derivatives(Q, s)
        delta = p - C
        first = (d.transpose() * P * delta)[0, 0]
        second = (d.transpose() * P * d + dd.transpose() * P * delta)[0, 0]
        if second <= 0:
            break
        new = max(F(0), min(F(1), s - first / second))
        if abs(new - s) < F(1, scale):
            break
        if distance(new) > distance(s):
            new = (new + s) / 2
        s = new
    best = min(
        (((C - curve_at(Q, s)).transpose() * P * (C - curve_at(Q, s)))[0, 0], s)
        for s in candidates
    )
    need(best[0] >= 0, "negative exact metric distance")
    norm = best[0] / (R * R)
    return {
        "inside": norm <= 1,
        "parameter": str(best[1]),
        "squared_norm": str(norm),
        "method": "exact_rational_curve_witness; nonadmission_is_conservative",
    }


def membership(certificate, state):
    result = membership_details(certificate, state)
    return result["inside"], result["squared_norm"]
