"""Native A_CI selected-root equations and complete implicit C/logW derivative."""

from functools import lru_cache

from .grc_v4_codec import canonical_json_bytes
from .grc_v4_exact import exact_number
from .grc_v4_spark_aos_math import AOSMath
from .grc_v4_spark_cos import _matrix, _norm_inf, _reference_facts
from .grc_v4_spark_cpc import need, norm
from .grc_v4_spark_state import flint_operation, rational
from .grc_v4_state import FrozenJSONMap

ROOT_DOMAIN = "aci_quartic_C_W_flat_inf_ball_1_over_32_v1"
PROPOSAL_BITS = 224


@lru_cache(maxsize=16)
@flint_operation
def root_domain(graph_bytes):
    facts = _reference_facts(graph_bytes)
    B, O = _matrix(facts[0]), _matrix(facts[3])
    ell, S = _norm_inf(B.transpose() * B), _norm_inf(O) / 8
    r = exact_number(1, 32)
    h = S * r * r
    need(h < 1, "A_CI H inverse root domain")
    u = 1 / (1 - h)
    wl, wh = exact_number(99, 100), exact_number(101, 100)
    j = wh * (12 + 4 * ell * wh / 64 + 4 * ell * h / 64) / 1024
    g = 1 - (8 + 192 + j * j) / 65536
    need(g > exact_number(1, 2), "A_CI root floor premise")
    a = max(wh - g, 1 - wl) / (wl + g)
    den = 1 - a / 4
    J = j / den
    image = u * a * J / 2
    jH = 4 * wh * ell / 65536
    qj = 4 * wh * j / (65536 * (wl + g) ** 2)
    Jj = 1 / den + j * qj / (4 * den * den)
    FH = u * ((a * Jj + J * qj) * jH / 2 + image)
    rate = 2 * S * r * FH
    need(image < r and rate < 1, "A_CI uniform root self-map/contraction")
    return FrozenJSONMap(
        {
            "domain_id": ROOT_DOMAIN,
            "resource_box": ["0", "4"],
            "conductance_box": ["99/100", "101/100"],
            "flat_radius": str(r),
            "overlap_row_sum": str(S),
            "edge_laplacian_norm": str(ell),
            "H_deviation": str(h),
            "H_inverse": str(u),
            "baseline_current": str(j),
            "drive_lower": str(g),
            "q_absolute": str(a),
            "closure_denominator_lower": str(den),
            "selected_current": str(J),
            "image_bound": str(image),
            "baseline_H_lipschitz": str(jH),
            "q_baseline_lipschitz": str(qj),
            "current_baseline_lipschitz": str(Jj),
            "flat_H_lipschitz": str(FH),
            "contraction": str(rate),
            "uniqueness": "one root in the declared flat ball",
        }
    )


class ACIMath(AOSMath):
    def __init__(self, graph):
        super().__init__(graph)
        self.domain = root_domain(canonical_json_bytes(graph.to_payload()))
        self.root_q = self.scalar(rational(self.domain["contraction"]))

    def root(self, C, L, W=None, limit=60):
        W = self.exp(L) if W is None else W
        need(all(0 <= x <= 4 for x in C.entries()), "A_CI resource root box")
        need(
            all(self.q(99, 100) <= x <= self.q(101, 100) for x in W.entries()),
            "A_CI W root box",
        )
        cp = self.matrix([[x.mid()] for x in C.entries()])
        wp = self.matrix([[x.mid()] for x in W.entries()])
        rows = self.rows(cp, wp)
        flat = self.matrix(self.m, 1)
        for iteration in range(limit):
            read = self.read(cp, wp, self.geometry(flat), rows)
            if norm(read["causal_flat"] - flat) < self.scalar(2) ** (-PROPOSAL_BITS):
                break
            flat = self.matrix([[x.mid()] for x in read["causal_flat"].entries()])
            need(norm(flat) < self.q(1, 32), "A_CI proposal leaves root ball")
        else:
            raise RuntimeError("A_CI root proposal iteration limit")
        actual_rows = self.rows(C, W)
        read = self.read(C, W, self.geometry(flat), actual_rows)
        residual = norm(read["causal_flat"] - flat)
        error = (residual / (1 - self.root_q)).upper()
        need(norm(flat) + error < self.q(1, 32), "A_CI enclosure leaves root ball")
        enclosed = self.matrix(
            [[self.scalar(x.fmpq(), error.fmpq())] for x in flat.entries()]
        )
        H = self.geometry(enclosed)
        selected = self.read(C, W, H, actual_rows)
        coefficient = self.scalar(
            sum((self.rational(x, 8)) ** 2 for row in self.overlap for x in row)
        ).sqrt()
        joint = coefficient * (2 * norm(flat) * residual + residual**2)
        return {
            "flat": enclosed,
            "proposal": flat,
            "geometry": H,
            "selected": selected,
            "residual": residual,
            "root_error": error,
            "joint_residual_upper": joint,
            "iterations": iteration + 1,
            "_C": C,
            "_L": L,
            "_W": W,
        }

    def advance(self, C, L, root):
        need(C is root["_C"] and L is root["_L"], "A_CI root subject changed")
        J = root["selected"]["current"]
        after = C - 32 * self.B * J
        exponent, _ = self.exponent(after, root["_W"], J)
        return after, self.decay * L + (1 - self.decay) * exponent

    def step(self, C, L):
        root = self.root(C, L)
        after, ln = self.advance(C, L, root)
        return dict(root, after=after, logW_after=ln)

    def flat_partials(self, C, W, flat, rows=None):
        H = self.geometry(flat)
        selected = self.read(C, W, H, rows)
        dHs = [
            self.matrix(
                [
                    [
                        self.overlap[i][j]
                        * (
                            (flat[j, 0] if i == k else 0)
                            + (flat[i, 0] if j == k else 0)
                        )
                        / 8
                        for j in range(self.m)
                    ]
                    for i in range(self.m)
                ]
            )
            for k in range(self.m)
        ]
        pack = lambda columns: self.matrix(
            [[columns[j][i, 0] for j in range(self.m)] for i in range(self.m)]
        )
        dj0 = (
            -self.diag(W)
            * self.Bt
            * self.B
            * pack([dH * self.Bt * C for dH in dHs])
            / 65536
        )
        j0, G, q, J = (selected[k] for k in ("baseline", "drive", "q", "current"))
        dq = self.matrix(
            [
                [
                    4
                    * W[i, 0]
                    * G[i, 0]
                    * j0[i, 0]
                    * dj0[i, j]
                    / (65536 * (W[i, 0] + G[i, 0]) ** 2)
                    for j in range(self.m)
                ]
                for i in range(self.m)
            ]
        )
        dJ = self.matrix(
            [
                [
                    dj0[i, j] / (1 - q[i, 0] / 4)
                    + j0[i, 0] * dq[i, j] / (4 * (1 - q[i, 0] / 4) ** 2)
                    for j in range(self.m)
                ]
                for i in range(self.m)
            ]
        )
        df = H.solve(
            (self.diag(q) * dJ + self.diag(J) * dq) / 2
            - pack([dH * selected["causal_flat"] for dH in dHs])
        )
        return selected, H, df, dJ

    def jacobian(self, C, L, root=None):
        root = self.root(C, L) if root is None else root
        need(
            C is root["_C"] and L is root["_L"], "A_CI derivative root subject changed"
        )
        W = root["_W"]
        d = self.n + self.m
        dC = self.matrix([[int(i == j) for j in range(d)] for i in range(self.n)])
        dL = self.matrix(
            [[int(self.n + i == j) for j in range(d)] for i in range(self.m)]
        )
        dW = self.diag(W) * dL
        rows = self.rows(C, W, dC, dW)
        selected, H, Ff, Jf = self.flat_partials(C, W, root["flat"], rows)
        need(norm(Ff) < self.root_q, "A_CI implicit derivative root bound")
        zero = self.matrix(self.m, self.m)
        Jx, qx = self.read_derivative(C, W, H, selected, dC, dW, [zero] * d, rows)
        Fx = H.solve(
            (self.diag(selected["q"]) * Jx + self.diag(selected["current"]) * qx) / 2
        )
        df = (self.I - Ff).solve(Fx)
        dJ = Jx + Jf * df
        after = C - 32 * self.B * selected["current"]
        da = dC - 32 * self.B * dJ
        _, de = self.exponent(after, W, selected["current"], None, da, dW, dJ)
        return self.matrix(
            da.tolist() + (self.decay * dL + (1 - self.decay) * de).tolist()
        )
