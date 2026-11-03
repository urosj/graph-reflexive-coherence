"""Native full C/64 log W continuous-domain proof for A_RG2b.

Recompute exact Bernstein cells, order-four interval Taylor residuals, both
geometry consumers and the writer. No trajectory or section derivative is an
input. The physical domain has 14 independent C and 16 conductance directions.
"""

import itertools
import time
from functools import lru_cache
from math import comb

from flint import arb, arb_mat, arb_series, ctx, fmpq, fmpq_mat

from .grc_9_v4_completion_crg2b import (
    CurveBounds,
    bernstein_cells,
    cheb_times_x,
    curve_at,
    curve_derivatives,
    positive_definite_exact,
    split_bernstein,
)
from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_codec import canonical_json_bytes
from .grc_v4_spark_arg2b_math import (
    DT,
    SCALE,
    ARG2bMath,
    ball,
    graph_constants,
    infnorm,
    need,
)
from .grc_v4_spark_conductance import ExactConductanceState
from .grc_v4_spark_crg2b_math import exact_bounds, norm_upper
from .grc_v4_spark_state import flint_operation, rational
from .grc_v4_state import FrozenJSONMap

F = fmpq
RADIUS = F(1, 4096)
DECAY = F(999, 1000)
DEGREE = 40
GEOMETRY_DEPTH = 6
RESIDUAL_LIMIT = F(1, 10**7)
MAX_RESIDUAL_DEPTH = 16
REFERENCE_LOWER = F(1, 4)
TAYLOR_ORDER = 4


def metric(m):
    B = graph_constants(m.key)[0]
    A = B * B.transpose()
    n = m.n
    pi = fmpq_mat([[fmpq(1, n) for _ in range(n)] for _ in range(n)])
    P = (A + pi).inv()
    trace = sum(P[i, i] for i in range(n)) - 1
    need(A * P * A == A and trace > 0, "exact charge metric")
    m.algebra = {"A": A, "P": P}
    m.A = arb_mat(A)
    m.P = arb_mat(P)
    m.trace = arb(trace)
    m.amax = arb(infnorm(A))
    return A, P


def metric_norm(m, X):
    C = arb_mat([[X[i, 0]] for i in range(m.n)])
    Y = arb_mat([[X[m.n + i, 0]] for i in range(m.m)])
    square = (C.transpose() * m.P * C)[0, 0]
    return max(square.nonnegative_part().sqrt().upper(), norm_upper(Y).upper())


def ranges(rows):
    return arb_mat(
        [[arb((min(row) + max(row)) / 2, (max(row) - min(row)) / 2)] for row in rows]
    )


def composition(Q, rho):
    d = Q.ncols() - 1
    rows = [[fmpq(1)], [rho - 1, rho]]
    for _ in range(1, d):
        old = rows[-1]
        new = cheb_times_x(old)
        for j in range(len(new)):
            new[j] = (
                2 * rho * new[j]
                + (2 * (rho - 1) * old[j] if j < len(old) else 0)
                - (rows[-2][j] if j < len(rows[-2]) else 0)
            )
        rows.append(new)
    return Q * fmpq_mat(
        [
            [rows[i][j] if j < len(rows[i]) else 0 for j in range(d + 1)]
            for i in range(d + 1)
        ]
    )


def curve_jets(cell, width, *, at_midpoint):
    """Exact Bernstein derivatives/k! at the midpoint or over the whole cell."""
    degree = len(cell[0]) - 1
    out = []
    for row in cell:
        coefficients = []
        differences = list(row)
        for k in range(TAYLOR_ORDER + 1):
            factor = fmpq(comb(degree, k)) / width**k
            if at_midpoint:
                d = len(differences) - 1
                value = (
                    sum(fmpq(comb(d, i), 2**d) * z for i, z in enumerate(differences))
                    * factor
                )
                coefficients.append(arb(value))
            else:
                lo, hi = min(differences) * factor, max(differences) * factor
                coefficients.append(arb((lo + hi) / 2, (hi - lo) / 2))
            differences = [b - a for a, b in itertools.pairwise(differences)]
        out.append(arb_series(coefficients, prec=TAYLOR_ORDER + 1))
    return out


def reference_jets(m, X):
    """Independent scalar edge equations for the complete fixed-I map."""
    zero = lambda: arb_series([0], prec=TAYLOR_ORDER + 1)
    C = X[: m.n]
    Y = X[m.n :]
    W = [(v / ball(SCALE)).exp() for v in Y]
    lap = [zero() for _ in C]
    for k, (i, j) in enumerate(m.pairs):
        z = W[k] * (C[i] - C[j])
        lap[i] += z
        lap[j] -= z
    phi = [l / 64 - ((c - 2) ** 3 - (c - 2)) for l, c in zip(lap, C)]
    j0 = [-W[k] * (phi[i] - phi[j]) / 1024 for k, (i, j) in enumerate(m.pairs)]

    def exponent(c, current):
        rows = [
            [
                sum((W[k] * (c[j] - c[i]) for k, j in terms), zero())
                / sum((W[k] for k, j in terms), zero())
                if terms
                else zero()
                for terms in node
            ]
            for i, node in enumerate(m.terms)
        ]
        values = [
            -(
                c[i]
                + c[j]
                + sum(((a - b) ** 2 for a, b in zip(rows[i], rows[j])), zero())
                + current[k] ** 2
            )
            / 65536
            for k, (i, j) in enumerate(m.pairs)
        ]
        need(all(v[0] > m.floor_log for v in values), "jet floor branch")
        return values

    G = [v.exp() for v in exponent(C, j0)]
    q = [(w - g) / (w + g) for w, g in zip(W, G)]
    J = [j / (1 - v / 4) for j, v in zip(j0, q)]
    after = list(C)
    for k, (i, j) in enumerate(m.pairs):
        after[i] = after[i] - ball(DT) * J[k]
        after[j] = after[j] + ball(DT) * J[k]
    ex = exponent(after, J)
    return after + [
        m.decay * y + (1 - m.decay) * ball(SCALE) * v for y, v in zip(Y, ex)
    ]


def continuous_residual(m, Q):
    """Fourth-order Taylor enclosure on an exact partition; no sampling proof."""
    start = time.monotonic()
    shift = composition(Q, fmpq(str(DECAY)))
    initial = 6
    count = 2**initial
    cells = bernstein_cells(Q, initial)
    shiftcells = bernstein_cells(shift, initial)
    pending = [
        (fmpq(i, count), fmpq(i + 1, count), cells[i], shiftcells[i], initial)
        for i in reversed(range(count))
    ]
    leaves = []
    evaluations = 0
    maximum = arb(0)
    while pending:
        need(
            time.monotonic() - start < 120,
            "bounded continuous certificate evaluation limit",
        )
        lo, hi, cell, shiftcell, depth = pending.pop()
        mid = (lo + hi) / 2
        width = hi - lo
        cb = ranges(cell)
        need(m.in_agreement(cb), "reference curve leaves agreement")
        point = reference_jets(m, curve_jets(cell, width, at_midpoint=True))
        point_shift = curve_jets(shiftcell, width, at_midpoint=True)
        whole = reference_jets(m, curve_jets(cell, width, at_midpoint=False))
        whole_shift = curve_jets(shiftcell, width, at_midpoint=False)
        bound = arb(0)
        for k in range(TAYLOR_ORDER + 1):
            a, b = (whole, whole_shift) if k == TAYLOR_ORDER else (point, point_shift)
            coefficient = arb_mat([[x[k] - y[k]] for x, y in zip(a, b)])
            bound += metric_norm(m, coefficient) * arb(width / 2) ** k
        bound = bound.upper()
        evaluations += 1
        if bound < ball(RESIDUAL_LIMIT):
            maximum = max(maximum, bound)
            leaves.append(
                {"interval": [str(lo), str(hi)], "residual_upper": exact_bounds(bound)}
            )
        else:
            need(depth < MAX_RESIDUAL_DEPTH, "functional residual subdivision limit")
            a = [split_bernstein(row) for row in cell]
            b = [split_bernstein(row) for row in shiftcell]
            pending.append((mid, hi, [v[1] for v in a], [v[1] for v in b], depth + 1))
            pending.append((lo, mid, [v[0] for v in a], [v[0] for v in b], depth + 1))
    need(
        sum(fmpq(row["interval"][1]) - fmpq(row["interval"][0]) for row in leaves) == 1,
        "partition length",
    )
    need(
        leaves[0]["interval"][0] == "0"
        and leaves[-1]["interval"][1] == "1"
        and all(
            a["interval"][1] == b["interval"][0] for a, b in itertools.pairwise(leaves)
        ),
        "exact gap-free partition",
    )
    return maximum, {
        "method": "rational_Bernstein_derivatives_and_full_writer_order4_interval_Taylor",
        "evaluations": evaluations,
        "cells": leaves,
        "uniform_bound": exact_bounds(maximum),
        "continuous_parameter": True,
    }


def physical_bounds(m, Xbox):
    """P/Euclidean block norm, pointwise self-adjoint reference and section differences."""
    C, L = m.unpack(Xbox)
    W = m.exp(L)
    n = m.n
    A, P = m.algebra["A"], m.algebra["P"]
    curv = [3 * (x - 2) ** 2 - 1 for x in C.entries()]
    low = (
        fmpq_mat(
            [
                [curv[i].lower().fmpq() if i == j else 0 for j in range(n)]
                for i in range(n)
            ]
        )
        - A / 64
    )
    high = (
        fmpq_mat(
            [
                [curv[i].upper().fmpq() if i == j else 0 for j in range(n)]
                for i in range(n)
            ]
        )
        - A / 64
    )
    E = fmpq_mat(
        [[int(i == j) if i < n - 1 else -1 for j in range(n - 1)] for i in range(n)]
    )
    lower = positive_definite_exact(
        E.transpose() * (low - fmpq(str(REFERENCE_LOWER)) * P) * E
    )
    upper = positive_definite_exact(E.transpose() * (64 * P - high) * E)
    q0 = max(
        abs(1 - ball(DT / 1024) * ball(REFERENCE_LOWER)), abs(1 - ball(DT / 1024) * 64)
    )
    value = m.bounds["section_value_radius"]
    lip = ball(m.domain["image_lipschitz"])
    H = arb_mat(
        [
            [
                arb(int(i == j), value.upper().fmpq()) if m.overlap[i][j] else arb(0)
                for j in range(m.m)
            ]
            for i in range(m.m)
        ]
    )
    read = m.lag(Xbox, H)
    r = read["selected"]
    q = r["q"]
    j0 = r["baseline"]
    G = r["drive"]
    den = [1 - q[i, 0] / 4 for i in range(m.m)]
    R = m.diag(arb_mat([[W[i, 0] / den[i]] for i in range(m.m)]))
    D0 = m.A / 64 - m.diag(arb_mat([[v] for v in curv]))
    perturb_potential = m.B * (m.diag(W) - m.I + H - m.I) * m.Bt / 64
    dc = arb_mat([[int(i == j) for j in range(n)] for i in range(n)])
    dw = arb_mat(m.m, n)
    dphi = D0 + perturb_potential
    dj0 = -m.diag(W) * m.Bt * dphi / 1024
    _, de = m.exponent(C, W, j0, None, dc, dw, dj0)
    dq = arb_mat(
        [
            [
                -2 * W[i, 0] * G[i, 0] * de[i, j] / (W[i, 0] + G[i, 0]) ** 2
                for j in range(n)
            ]
            for i in range(m.m)
        ]
    )
    difference = (
        ball(DT / 1024) * m.B * ((R - m.I) * m.Bt * D0 + R * m.Bt * perturb_potential)
    )
    difference -= (
        ball(DT)
        * m.B
        * m.diag(arb_mat([[j0[i, 0] / (4 * den[i] ** 2)] for i in range(m.m)]))
        * dq
    )
    J = m.fixed_jacobian(Xbox, H, read)
    block = lambda a, b, c, d: arb_mat(
        [[J[i, j] for j in range(c, d)] for i in range(a, b)]
    )
    cc = q0 + norm_upper(difference) * (m.amax * m.trace).sqrt()
    cw = norm_upper(block(0, n, n, m.d)) * m.trace.sqrt()
    wc = norm_upper(block(n, m.d, 0, n)) * m.amax.sqrt()
    ww = m.decay + norm_upper(block(n, m.d, n, m.d) - m.decay * m.I)
    fixed = max((cc + cw).upper(), (wc + ww).upper())
    out_convert = max((n * m.trace).sqrt().upper(), arb(m.m).sqrt().upper())
    in_convert = max(m.amax.sqrt().upper(), arb(1))
    section = (out_convert * m.bounds["A_H"] * lip * in_convert).upper()
    correction = (out_convert * m.bounds["A_H"] * value).upper()
    contraction = (fixed + section).upper()
    need(contraction < 1, "full physical C/W curve contraction")
    return (
        contraction,
        correction,
        {
            "contraction": exact_bounds(contraction),
            "reference_contraction": exact_bounds(q0),
            "block_bounds": {
                k: exact_bounds(v)
                for k, v in {"CC": cc, "CW": cw, "WC": wc, "WW": ww}.items()
            },
            "section_lipschitz": exact_bounds(lip),
            "section_difference_correction": exact_bounds(section),
            "geometry_value_correction": exact_bounds(correction),
            "relative_dimension": n - 1 + m.m,
            "resource_dimension": n - 1,
            "conductance_dimension": m.m,
            "section_C1_claimed": False,
            "exact_ldl_pivots": {"lower": lower, "upper": upper},
            "charge_tangent_rayleigh_bounds": [str(REFERENCE_LOWER), "64"],
            "both_H_consumers": True,
            "full_writer_included": True,
            "all_independent_coordinates": True,
        },
    )


def geometry(kernel, policy, bounds, center, correction):
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
            if neighbors:
                low, high = (low - correction).lower(), (high + correction).upper()
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


def _verify_uncached(data):
    from .grc_9_v4_completion_certificate import binding
    from .grc_9_v4_completion_codec import CompletionPolicy, digest
    from .grc_v4_geometry import GRCV4Graph
    from .grc_v4_spark import quartic_kernel, quartic_profile

    need(
        set(data)
        == {
            "schema_version",
            "binding",
            "center",
            "logW_center",
            "curve",
            "radius",
            "parameter_decay",
            "subdivision_depth",
        },
        "closed joint curved operands",
    )
    need(
        data["schema_version"] == "grc9v4-native-arg2b-curve-operands-v1",
        "joint curve schema",
    )
    b = data["binding"]
    k = quartic_kernel(
        GRCV4Graph.from_payload(b["graph"]), quartic_profile(b["profile"])
    )
    policy = CompletionPolicy.from_payload(b["policy"])
    need(
        k.profile.FAMILY == "A_RG2b"
        and policy.numerical_policy_id == k.profile.NUMERICS
        and policy.step_duration == "16"
        and b == binding(k, policy, b["role"], b["charge"]),
        "full joint equation/role/duration binding",
    )
    Q = fmpq_mat(data["curve"])
    n = len(k.graph.live_node_ids)
    edges = len(k.graph.live_edge_ids)
    need(
        (n, edges, Q.nrows(), Q.ncols()) == (15, 16, 31, 41)
        and data["radius"] == "1/4096"
        and data["parameter_decay"] == "999/1000"
        and data["subdivision_depth"] == 6,
        "declared joint continuous domain",
    )
    need(
        all(
            sum(Q[i, j] for i in range(n)) == (rational(b["charge"]) if j == 0 else 0)
            for j in range(41)
        ),
        "exact coefficient charge identity",
    )
    origin = curve_at(Q, 0)
    need(
        tuple(map(str, origin.entries()[:n])) == tuple(data["center"])
        and tuple(str(x / SCALE) for x in origin.entries()[n:])
        == tuple(data["logW_center"]),
        "joint curve origin",
    )
    with _ARB_CONTEXT_LOCK, ctx.workprec(k.precision_bits):
        m = k.section_math()
        _, P = metric(m)
        # The diagnostic centre is an exact represented W state. Its rounded
        # exponential is used only for the spatial roster comparison.
        weights = tuple(
            str(arb(rational(x)).exp().mid().fmpq()) for x in data["logW_center"]
        )
        center = ExactConductanceState(
            k.graph, tuple(data["center"]), b["charge"], weights
        )
        bounds = CurveBounds(m, Q, RADIUS, 6)
        cb = bounds.box()
        yb = []
        for i in range(n, m.d):
            lo = min(min(cell[i]) for cell in bounds.cells) - RADIUS
            hi = max(max(cell[i]) for cell in bounds.cells) + RADIUS
            yb.append([arb((lo + hi) / 2, (hi - lo) / 2)])
        box = arb_mat(cb.tolist() + yb)
        need(
            m.in_agreement(box) and all(x > 0 for x in cb.entries()),
            "whole continuous tube agreement and positivity",
        )
        C, L = m.unpack(box)
        W = m.exp(L)
        wl = min(x.lower() for x in W.entries())
        deviation = max(abs(x - 1).upper() for x in W.entries())
        span = max(x.upper() for x in C.entries()) - min(x.lower() for x in C.entries())
        correction = 2 * deviation * span / wl
        geometric = geometry(k, policy, bounds, center, correction)
        geometric["weighted_row_correction"] = exact_bounds(correction)
        q, Herror, physical = physical_bounds(m, box)
        reference, partition = continuous_residual(m, Q)
        defect = (reference + Herror).upper()
        margin = ((1 - q) * ball(RADIUS) - defect).lower()
        need(0 < q < 1 and margin > 0, "joint domain strict self-map")
        numeric = k.uniform_metric_error(P, str(margin.fmpq()))
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
                "residual_partition": partition,
                "physical_difference_bound": physical,
                "geometry": geometric,
                "relative_dimension": 30,
                "full_physical_state": ["C", "W_A"],
                "coordinate_system": "C_then_64_logW",
                "all_parameters_certified_continuously": True,
                "section_C1_claimed": False,
                "future_trajectory_required": False,
                "supporting_trajectory_steps_after_completion": 0,
                "precision_bits": k.precision_bits,
                "metric": "max(charge_tangent_P_norm,64logW_Euclidean_norm)",
                "operands_digest": digest(data),
            }
        )


@lru_cache(maxsize=16)
def _common_verify(raw):
    from .grc_v4_codec import decode_canonical_json

    return _verify_uncached(decode_canonical_json(raw))


def verify(data):
    from .grc_9_v4_completion_codec import digest

    need(data["binding"]["role"] in ("current", "reset"), "explicit certificate role")
    common = FrozenJSONMap(data).to_dict()
    common["binding"]["role"] = "current"
    proof = _common_verify(canonical_json_bytes(common)).to_dict()
    # Only the role is removed from the numerical cache key. Its original
    # binding and the full operands digest remain mandatory on publication.
    proof["operands_digest"] = digest(data)
    return FrozenJSONMap(proof)


@lru_cache(maxsize=16)
def _grid(rows):
    Q = fmpq_mat(rows)
    return tuple(tuple(map(str, curve_at(Q, fmpq(i, 64)).entries())) for i in range(65))


@lru_cache(maxsize=16)
@flint_operation
def membership_details(certificate, state):
    b = certificate.operands["binding"]
    need(
        type(state) is ExactConductanceState
        and state.graph.to_payload() == b["graph"].to_dict()
        and state.charge == b["charge"],
        "full graph/charge/C/W membership subject",
    )
    with _ARB_CONTEXT_LOCK, ctx.workprec(certificate.proof["precision_bits"]):
        m = ARG2bMath(state.graph)
        _, P = metric(m)
        Q = fmpq_mat(certificate.operands["curve"])
        C = fmpq_mat([[rational(x)] for x in state.C])
        Y = arb_mat([[SCALE * arb(rational(w)).log()] for w in state.W_A])
        R = rational(certificate.operands["radius"])

        def distances(s, point=None):
            point = (
                curve_at(Q, s)
                if point is None
                else fmpq_mat([[rational(x)] for x in point])
            )
            dc = C - fmpq_mat([[point[i, 0]] for i in range(m.n)])
            dy = Y - arb_mat([[point[m.n + i, 0]] for i in range(m.m)])
            a = arb((dc.transpose() * P * dc)[0, 0])
            d = sum(x * x for x in dy.entries()).nonnegative_part()
            return a, d

        def score(s, point=None):
            a, d = distances(s, point)
            return max(a.upper().fmpq(), d.upper().fmpq())

        endpoints = [(score(s), s) for s in (F(0), F(1))]
        best = min(endpoints)
        if best[0] > R**2:
            grid = _grid(tuple(tuple(r) for r in certificate.operands["curve"]))
            best = min(
                (score(F(i, 64), point), F(i, 64)) for i, point in enumerate(grid)
            )
            s = best[1]
            candidates = {F(0), F(1), s}
            scale = 2**32
            # Minimise a smooth sum to propose s only; exact full C distance
            # and outward log-W distance are the sole admission inequalities.
            for _ in range(12):
                s = F((s.numerator * scale) // s.denominator, scale)
                candidates.add(s)
                p, d, dd = curve_derivatives(Q, s)
                cp = lambda V: fmpq_mat([[V[i, 0]] for i in range(m.n)])
                yp = lambda V: arb_mat([[V[m.n + i, 0]] for i in range(m.m)])
                delta = cp(p) - C
                dy = yp(p) - Y
                first = (
                    arb((cp(d).transpose() * P * delta)[0, 0])
                    + (yp(d).transpose() * dy)[0, 0]
                )
                second = (
                    arb(
                        (
                            cp(d).transpose() * P * cp(d)
                            + cp(dd).transpose() * P * delta
                        )[0, 0]
                    )
                    + (yp(d).transpose() * yp(d) + yp(dd).transpose() * dy)[0, 0]
                )
                if not second > 0:
                    break
                new = max(F(0), min(F(1), s - (first / second).mid().fmpq()))
                if abs(new - s) < F(1, scale):
                    break
                if score(new) > score(s):
                    new = (s + new) / 2
                s = new
            best = min((score(s), s) for s in candidates)
        upper = best[0] / R**2
        return {
            "inside": upper <= 1,
            "parameter": str(best[1]),
            "squared_norm": str(upper),
            "method": "exact_C_and_outward_logW_curve_witness; nonadmission_is_conservative",
        }


def membership(certificate, state):
    value = membership_details(certificate, state)
    return value["inside"], value["squared_norm"]
