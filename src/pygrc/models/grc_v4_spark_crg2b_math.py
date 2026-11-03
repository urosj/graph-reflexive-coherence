"""Native quartic C_RG2b completion and finite-chain section enclosure.

Only partial derivatives of smooth two-input maps are used. The invariant section
is Lipschitz. Cached operands are immutable exact graph facts, never trajectories.
"""

import json
from functools import lru_cache

from flint import arb, arb_mat, ctx, fmpq, fmpq_mat

from .grc_v4_certification import CertificationInconclusive
from .grc_v4_spark_cos import _matrix, _norm_inf, _reference_facts, _rows
from .grc_v4_state import FrozenJSONMap

F = fmpq
ETA = F(1, 1024)
DT = F(8)
RHO = F(1, 1024)
LIP = F(1, 256)
DEPTH = 32
SWEEPS = 8
NEWTON_LIMIT = 12
PROPOSAL_BITS = 224
PRECISION = 256
COMPLETION_ID = "quartic_crg2b_bounded_increment_argument_retraction_duration8_v1"
APPROXIMATION_ID = "quartic_crg2b_arb256_chain32_newton12_sweeps8_current160_v1"
DOMAIN_ID = "quartic_crg2b_graph_bound_signed_nested_charts_v1"
ERROR_NORM = "induced_infinity_symmetric_star_v1"


def need(ok, message):
    if not ok:
        raise CertificationInconclusive(message)


def fraction(x):
    return F(x)


def ball(x):
    return arb(F(x))


def exact_bounds(x):
    return [str(x.lower().fmpq()), str(x.upper().fmpq())]


def midpoint(M):
    return arb_mat([[x.mid() for x in row] for row in M.tolist()])


def maxnorm(M):
    return arb(
        max(
            sum(abs(M[i, j]).upper().fmpq() for j in range(M.ncols()))
            for i in range(M.nrows())
        )
    )


def norm_upper(M):
    return sum(x * x for x in M.entries()).nonnegative_part().sqrt().upper()


@lru_cache(maxsize=16)
def _algebra_facts(encoded):
    B, I, D, O, M = (_matrix(x) for x in _reference_facts(encoded.encode())[:5])
    A = B * (I + M / 4) * B.transpose()
    L = B * B.transpose()
    n = B.nrows()
    pi = fmpq_mat([[F(1, n) for _ in range(n)] for _ in range(n)])
    P = (A + pi).inv()
    trace = sum(P[i, i] for i in range(n)) - 1
    need(trace > 0 and A * P * A == A, "exact charge metric identity")
    return FrozenJSONMap(
        {
            "B": _rows(B),
            "D": _rows(D),
            "I": _rows(I),
            "M": _rows(M),
            "A": _rows(A),
            "L": _rows(L),
            "P": _rows(P),
            "trace": str(trace),
            "overlap": [
                [int(O[i, j]) for j in range(O.ncols())] for i in range(O.nrows())
            ],
            "a0": str(_norm_inf(M)),
            "amax": str(_norm_inf(A)),
            "AL": str(_norm_inf(A * L)),
            "b": str(_norm_inf(B)),
            "ell": str(_norm_inf(D)),
            "s": str(_norm_inf(O) / 8),
        }
    )


@lru_cache(maxsize=16)
def _matrix_facts(encoded):
    # Immutable exact scalars are cached, never mutable FLINT matrices. This
    # avoids reparsing thousands of rational strings at every section read.
    v = _algebra_facts(encoded)
    return tuple(
        (k, tuple(tuple(F(x) for x in row) for row in v[k]))
        for k in ("B", "D", "I", "M", "A", "L", "P")
    )


def graph_algebra(encoded):
    v = _algebra_facts(encoded)
    out = {k: fmpq_mat(rows) for k, rows in _matrix_facts(encoded)}
    out.update({k: v[k] if k == "overlap" else F(v[k]) for k in v if k not in out})
    return out


def polynomial_image(algebra, lo, hi):
    """Exact separable cubic map at H=I; interval extrema include critical roots."""
    A, L = algebra["A"], algebra["L"]
    AL = A * L
    n = A.nrows()
    h = ETA * DT
    out = []
    for i in range(n):
        lows = []
        highs = []
        for j in range(n):
            a = -h * fraction(A[i, j])
            b = F(i == j) + h * fraction(A[i, j]) + h * fraction(AL[i, j]) / 64
            xs = [ball(lo - 2), ball(hi - 2)]
            if a and -b / (3 * a) > 0:
                r = ball(-b / (3 * a)).sqrt()
                for x in (r, -r):
                    if not (x.upper() < ball(lo - 2) or x.lower() > ball(hi - 2)):
                        xs.append(x)
            vals = [ball(a) * x**3 + ball(b) * x for x in xs]
            lows.append(min(x.lower() for x in vals))
            highs.append(max(x.upper() for x in vals))
        out.append((2 + sum(lows), 2 + sum(highs)))
    return min(x[0] for x in out), max(x[1] for x in out)


@lru_cache(maxsize=16)
def global_domain(encoded, precision=256):
    """Fresh quartic bounds; physical agreement and nested domains are explicit."""
    g = json.loads(encoded)
    a = graph_algebra(encoded)
    source = len(g["live_node_ids"]) == 12
    need(source or len(g["live_node_ids"]) == 15, "only declared source/target graphs")
    u = F(3, 2) if source else F(33, 16)
    lo, hi = 2 - u, 2 + u
    b, ell, a0, an, al, s = (a[k] for k in ("b", "ell", "a0", "amax", "AL", "s"))
    need(a0 * RHO * ell < 1, "uniform current inverse")
    inverse = a0 / (1 - a0 * RHO * ell)
    hinv = 1 / (1 - RHO)
    h = ETA * DT
    site = max(u**3 - u, F(1))
    curv = max(3 * u * u - 1, F(1))
    span = 2 * u
    j0 = ETA * (2 * site + ell * (1 + RHO) * span / 64)
    j0x = ETA * (2 * curv + ell * (1 + RHO) * 2 / 64)
    j0h = ETA * ell * span / 64
    y = inverse * j0
    flat = hinv * y / 2
    fx = hinv * inverse * j0x / 2
    fh = hinv * (inverse * (j0h + ell * y) / 2 + flat)
    gx = 2 * s * flat * fx
    gh = 2 * s * flat * fh
    V = s * flat**2
    jh = j0h * (1 + inverse / 4) + inverse * ell * y / 4
    ah = DT * b * jh
    qdiff = inverse * RHO * ell * a0 / 4
    perturb = (
        h * b * 2 * (qdiff * (curv + 2 * b / 64) + (1 + inverse / 4) * 2 * b * RHO / 64)
    )
    ax = h * (an * curv + al / 64) + perturb
    mf = h * (an * site + al * u / 64) + ah * RHO
    ellbase = ax + ah * LIP
    inv = 1 / (1 - ellbase)
    image_lip = (gx + gh * LIP) * inv
    q = gh + (gx + gh * LIP) * inv * ah
    need(
        ellbase < 1 and V < RHO and image_lip <= LIP and q < 1,
        "quartic graph-transform premises",
    )
    with ctx.workprec(precision):
        if source:
            km = (F(7, 8), F(25, 8))
            k = (F(9, 16), F(55, 16))
            image = (ball(km[0] - mf), ball(km[1] + mf))
        else:
            km = (F(-1, 32), F(129, 32))
            k = (F(-3, 64), F(259, 64))
            left, right = polynomial_image(a, *km)
            image = (left - ball(ah * RHO), right + ball(ah * RHO))
        need(lo < k[0] < km[0] < km[1] < k[1] < hi, "strict nested signed charts")
        need(
            image[0] > ball(k[0]) and image[1] < ball(k[1]),
            "whole K_minus image containment",
        )
        spectrum = {
            "nonconstant_eigenvalue_lower": _reference_facts(encoded.encode())[-1]
        }
        need(
            (1 - RHO) * F(spectrum["nonconstant_eigenvalue_lower"]) > F(1, 64),
            "uniform H selector separation",
        )
        return FrozenJSONMap(
            {
                "schema": "native-spark-crg2b-domain-v1",
                "completion": "bounded_increment_argument_retraction_v1",
                "resource_agreement": [str(lo), str(hi)],
                "K_minus": list(map(str, km)),
                "K": list(map(str, k)),
                "contained_image": [
                    exact_bounds(image[0])[0],
                    exact_bounds(image[1])[1],
                ],
                "geometry_radius": str(RHO),
                "geometry_norm": "induced_infinity_symmetric_star",
                "section_lipschitz": str(LIP),
                "section_value_radius": str(V),
                "image_lipschitz": str(image_lip),
                "A_X": str(ax),
                "A_H": str(ah),
                "G_X": str(gx),
                "G_H": str(gh),
                "base_lipschitz": str(ellbase),
                "inverse_lipschitz": str(inv),
                "graph_transform_contraction": str(q),
                "section_tail": str(q**DEPTH * V),
                "current_inverse_norm": str(inverse),
                "hodge_inverse_norm": str(hinv),
                "reference_inverse_norm": str(a0),
                "incidence_norm": str(b),
                "edge_laplacian_norm": str(ell),
                "overlap_sum_over_8": str(s),
                "reference_resource_operator_norm": str(an),
                "reference_AL_norm": str(al),
                "global_displacement": str(mf),
                "selector": spectrum,
                "global_resource_box_invariance_claimed": False,
                "section_C1_claimed": False,
                "reference_zero_site_bounds_reused": False,
            }
        )


class SectionMath:
    def __init__(self, graph):
        self.graph = graph
        self.precision = ctx.prec
        self.key = json.dumps(graph, sort_keys=True, separators=(",", ":"))
        self.algebra = graph_algebra(self.key)
        self.domain = global_domain(self.key, ctx.prec)
        self.nodes = graph["live_node_ids"]
        self.n = len(self.nodes)
        self.m = len(graph["edges"])
        self.edges = [
            (e["tail"]["node_id"], e["head"]["node_id"]) for e in graph["edges"]
        ]
        self.B = arb_mat(self.algebra["B"])
        self.Bt = self.B.transpose()
        self.Le = arb_mat(self.algebra["D"])
        self.I = arb_mat(self.algebra["I"])
        self.overlap = self.algebra["overlap"]
        self.P = arb_mat(self.algebra["P"])
        self.A = arb_mat(self.algebra["A"])
        self.trace = arb(self.algebra["trace"])
        self.amax = ball(self.algebra["amax"])
        self.sqrtamax = self.amax.sqrt().upper()
        self.bounds = {
            k: ball(self.domain[k])
            for k in (
                "A_X",
                "A_H",
                "G_X",
                "G_H",
                "inverse_lipschitz",
                "graph_transform_contraction",
                "section_value_radius",
                "section_tail",
                "current_inverse_norm",
            )
        }
        self.lo, self.hi = map(F, self.domain["resource_agreement"])
        self.section_calls = 0
        self.lag_operator_builds = 0
        self.newton_iterations = 0
        self.read_count = 0
        self.identity_operators = {}
        self.proposal_sweeps = 0
        self.resource_identity = arb_mat(
            [[int(i == j) for j in range(self.n)] for i in range(self.n)]
        )
        self.star_pairs = tuple(
            (i, j)
            for i in range(self.m)
            for j in range(i, self.m)
            if self.overlap[i][j]
        )

    @staticmethod
    def q(a, b=1):
        return ball(F(a, b))

    def vector(self, values):
        return arb_mat([[ball(values[n])] for n in self.nodes])

    @staticmethod
    def site(C):
        return arb_mat([[(x - 2) ** 3 - (x - 2)] for x in C.entries()])

    def geometry(self, flat):
        H = arb_mat(self.I)
        for i, j in self.star_pairs:
            value = self.overlap[i][j] * flat[i, 0] * flat[j, 0] / 8
            if i == j:
                H[i, j] += value
            else:
                H[i, j] = H[j, i] = value
        return H

    def clip(self, C):
        rows = []
        lo, hi = self.lo, self.hi
        for x in C.entries():
            if x.rad() == 0:
                # Finite-chain proposals are exact dyadic points. Avoid two
                # endpoint conversions and a rebuilt interval at every Newton trial.
                q = x.fmpq()
                rows.append([x if lo <= q <= hi else arb(lo if q < lo else hi)])
            else:
                left = max(lo, min(hi, x.lower().fmpq()))
                right = max(lo, min(hi, x.upper().fmpq()))
                rows.append([arb((left + right) / 2, (right - left) / 2)])
        return arb_mat(rows)

    def operators(self, H):
        # Precision belongs to the cache key; no lower-precision operator reuse.
        if H == self.I and ctx.prec in self.identity_operators:
            return self.identity_operators[ctx.prec]
        M = (self.q(3, 4) * self.I + H * self.Le).inv()
        hi = H.inv()
        lh = self.B * H * self.Bt
        A = self.B * (self.I + M / 4) * self.Bt
        self.lag_operator_builds += 1
        out = {"H": H, "M": M, "Hi": hi, "L": lh, "A": A}
        if H == self.I:
            self.identity_operators[ctx.prec] = out
        return out

    def lag(self, C, ops, *, retract=False):
        c = self.clip(C) if retract else C
        phi = ops["L"] * c / 64 - self.site(c)
        j0 = -ball(ETA) * self.Bt * phi
        y = ops["M"] * j0
        J = j0 + y / 4
        flat = ops["Hi"] * y / 2
        H = self.geometry(flat)
        self.read_count += 1
        return {
            "increment": -ball(DT) * self.B * J,
            "geometry": H,
            "current": J,
            "causal_flat": flat,
            "baseline": j0,
        }

    def inverse_proposal(self, target, H, start):
        ops = self.operators(H)
        X = arb_mat(start)
        identity = self.resource_identity
        threshold = arb(2) ** (-PROPOSAL_BITS + 32)
        for iteration in range(NEWTON_LIMIT):
            c = self.clip(X)
            phi = ops["L"] * c / 64 - self.site(c)
            f = ball(ETA * DT) * ops["A"] * phi
            residual = X + f - target
            self.newton_iterations += 1
            if maxnorm(residual) < threshold:
                break
            DP = ops["L"] / 64
            for i in range(self.n):
                DP[i, i] -= 3 * (c[i, 0] - 2) ** 2 - 1
            for j, x in enumerate(X.entries()):
                if not self.lo < x.mid().fmpq() < self.hi:
                    for i in range(self.n):
                        DP[i, j] = 0
            jac = identity + ball(ETA * DT) * ops["A"] * DP
            X = midpoint(X - jac.solve(residual))
        else:
            raise CertificationInconclusive("declared inverse proposal iteration cap")
        return X, ops

    def section(self, C, *, retain_chain=False):
        need(
            ctx.prec == self.precision and C.nrows() == self.n and C.ncols() == 1,
            "section precision/subject",
        )
        need(
            all(x.rad() == 0 for x in C.entries()),
            "section query must be an exact proposed tube center",
        )
        need(
            all(ball(self.lo) < x < ball(self.hi) for x in C.entries()),
            "physical query outside completion agreement chart",
        )
        self.section_calls += 1
        with ctx.workprec(PROPOSAL_BITS):
            xs = [arb_mat(C) for _ in range(DEPTH + 1)]
            hs = [arb_mat(self.I) for _ in range(DEPTH + 1)]
            for _ in range(SWEEPS):
                self.proposal_sweeps += 1
                ops = []
                for i in range(1, DEPTH + 1):
                    xs[i], op = self.inverse_proposal(xs[i - 1], hs[i], xs[i])
                    ops.append(op)
                generated = [
                    midpoint(self.lag(xs[i], ops[i - 1], retract=True)["geometry"])
                    for i in range(1, DEPTH + 1)
                ]
                newhs = generated + [arb_mat(self.I)]
                change = max(maxnorm(a - b) for a, b in zip(hs, newhs))
                hs = newhs
                # Proposal-only early stop. Every level is subsequently
                # certified afresh at PRECISION, including both residuals. The
                # proposal goal is comfortably below current160; chasing the
                # much smaller depth-32 tail wastes sweeps. Admission remains
                # governed by the unchanged full-input current160/flux128 checks.
                slope = self.bounds["G_H"] + ball(LIP) * self.bounds["A_H"]
                if (
                    slope * change / (1 - self.bounds["graph_transform_contraction"])
                    < arb(2) ** -180
                ):
                    break
        need(xs[0] == C and hs[-1] == self.I, "finite section boundaries")
        rx = arb(0)
        rh = arb(0)
        levels = []
        for i in range(1, DEPTH + 1):
            H = hs[i]
            need(maxnorm(H - self.I) <= ball(RHO), "finite geometry ball")
            need(
                all(H[j, k] == H[k, j] for j in range(self.m) for k in range(self.m)),
                "finite geometry symmetry",
            )
            need(
                all(
                    H[j, k] == 0
                    for j in range(self.m)
                    for k in range(self.m)
                    if not self.overlap[j][k]
                ),
                "finite geometry support",
            )
            r = self.lag(xs[i], self.operators(H), retract=True)
            xr = maxnorm(xs[i] + r["increment"] - xs[i - 1])
            hr = maxnorm(hs[i - 1] - r["geometry"])
            rx = max(rx, xr)
            rh = max(rh, hr)
            if retain_chain:
                levels.append(
                    {
                        "X": [str(x.fmpq()) for x in xs[i].entries()],
                        "H": [
                            str(H[j, k].fmpq())
                            for j in range(self.m)
                            for k in range(j, self.m)
                            if self.overlap[j][k]
                        ],
                        "state_residual": exact_bounds(xr),
                        "geometry_residual": exact_bounds(hr),
                    }
                )
        # Backward elimination of the coupled residual inequalities. Each exact
        # finite-level section stays in the proved global Lipschitz class.
        L = ball(LIP)
        q = self.bounds["graph_transform_contraction"]
        residual_error = ((rh + L * rx) / (1 - q)).upper()
        tail = self.bounds["section_tail"]
        error = (residual_error + tail).upper()
        need(maxnorm(hs[0] - self.I) + error < ball(RHO), "returned section ball")
        H = arb_mat(self.m, self.m)
        for i in range(self.m):
            for j in range(i, self.m):
                if self.overlap[i][j]:
                    H[i, j] = arb(hs[0][i, j].fmpq(), error.fmpq())
                    H[j, i] = H[i, j]
        out = {
            "proposal": hs[0],
            "geometry": H,
            "error": error,
            "residual_error": residual_error,
            "tail": tail,
            "state_residual": rx,
            "geometry_residual": rh,
            "read": self.lag(C, self.operators(H)),
            "subject": C,
        }
        if retain_chain:
            out["chain"] = levels
        return out

    def enclose(self, C):
        """Extend a point-chain section proof to the complete input ball."""
        scale = 2**PROPOSAL_BITS
        qs = [x.mid().fmpq() for x in C.entries()]
        point = arb_mat(
            [[arb(F((q.numerator * scale) // q.denominator, scale))] for q in qs]
        )
        result = self.section(point, retain_chain=True)
        error = (result["error"] + ball(LIP) * maxnorm(C - point)).upper()
        H = arb_mat(self.m, self.m)
        for i in range(self.m):
            for j in range(i, self.m):
                if self.overlap[i][j]:
                    H[i, j] = arb(result["proposal"][i, j].fmpq(), error.fmpq())
                    H[j, i] = H[i, j]
        need(maxnorm(H - self.I) < ball(RHO), "whole-input section class")
        result.update(
            geometry=H, error=error, subject=C, read=self.lag(C, self.operators(H))
        )
        return result
