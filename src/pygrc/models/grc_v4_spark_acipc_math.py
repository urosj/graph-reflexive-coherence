"""Native composite A_CI_PC root and complete implicit C/logW/Z derivative."""

from functools import lru_cache
from math import isqrt

from .grc_v4_codec import canonical_json_bytes
from .grc_v4_exact import exact_number
from .grc_v4_spark_apc_math import APCMath
from .grc_v4_spark_cos import _matrix, _norm_inf, _reference_facts
from .grc_v4_spark_cpc import frobenius, need, norm
from .grc_v4_spark_state import flint_operation, rational
from .grc_v4_state import FrozenJSONMap

ROOT_DOMAIN = "acipc_quartic_C_W_Z_flat_inf_ball_1_over_32_carrier_1_over_64_v1"
PROPOSAL_BITS = 224


@lru_cache(maxsize=16)
@flint_operation
def root_domain(graph_bytes):
    facts = _reference_facts(graph_bytes)
    B, O = _matrix(facts[0]), _matrix(facts[3])
    ell, S = _norm_inf(B.transpose() * B), _norm_inf(O) / 8
    r = exact_number(1, 32)
    R = exact_number(1, 64)
    m = B.ncols()
    z = (isqrt(m - 1) + 1) * R / 2
    h = z + S * r * r
    need(h < 1, "A_CI_PC H inverse root domain")
    u = 1 / (1 - h)
    wl, wh = exact_number(99, 100), exact_number(101, 100)
    j = wh * (12 + 4 * ell * wh / 64 + 4 * ell * h / 64) / 1024
    g = 1 - (8 + 192 + j * j) / 65536
    need(g > exact_number(1, 2), "A_CI_PC root floor premise")
    a = max(wh - g, 1 - wl) / (wl + g)
    den = 1 - a / 4
    J = j / den
    image = u * a * J / 2
    jH = 4 * wh * ell / 65536
    qj = 4 * wh * j / (65536 * (wl + g) ** 2)
    Jj = 1 / den + j * qj / (4 * den * den)
    FH = u * ((a * Jj + J * qj) * jH / 2 + image)
    rate = 2 * S * r * FH
    need(image < r and rate < 1, "A_CI_PC uniform root self-map/contraction")
    source = exact_number(m, 2) * image * image
    writer = 1 - (200 + J * J) / 65536
    need(source < R and writer > wl, "composite history envelope")
    need(
        wl * (1 - R / 2) * rational(facts[-1]) > exact_number(1, 64),
        "composite selector gap",
    )
    return FrozenJSONMap(
        {
            "domain_id": ROOT_DOMAIN,
            "resource_box": ["0", "4"],
            "conductance_box": ["99/100", "101/100"],
            "flat_radius": str(r),
            "carrier_radius": str(R),
            "carrier_norm": "symmetric_star_frobenius_v1",
            "carrier_H_deviation": str(z),
            "H_eigenvalue_lower": str(1 - R / 2),
            "H_eigenvalue_upper": str(1 + R / 2 + exact_number(m, 4) * r * r),
            "source_norm_upper": str(source),
            "writer_drive_lower": str(writer),
            "invariant_carrier_ball": True,
            "resource_box_invariance_claimed": False,
            "stationary_composite_gain": 2,
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


class ACIPCMath(APCMath):
    def __init__(self, graph):
        super().__init__(graph)
        self.domain = root_domain(canonical_json_bytes(graph.to_payload()))
        self.root_q = self.scalar(rational(self.domain["contraction"]))

    def composite_geometry(self, flat, Z):
        return self.I + (Z + self.source(flat)) / 2

    def root(self, C, L, Z, W=None, limit=60):
        W = self.exp(L) if W is None else W
        need(all(0 <= x <= 4 for x in C.entries()), "A_CI_PC resource root box")
        need(
            all(self.q(99, 100) <= x <= self.q(101, 100) for x in W.entries()),
            "A_CI_PC W root box",
        )
        need(frobenius(Z) <= self.q(1, 64), "composite incoming carrier ball")
        zp = self.matrix([[x.mid() for x in row] for row in Z.tolist()])
        cp = self.matrix([[x.mid()] for x in C.entries()])
        wp = self.matrix([[x.mid()] for x in W.entries()])
        rows = self.rows(cp, wp)
        flat = self.matrix(self.m, 1)
        for iteration in range(limit):
            read = self.read(cp, wp, self.composite_geometry(flat, zp), rows)
            if norm(read["causal_flat"] - flat) < self.scalar(2) ** (-PROPOSAL_BITS):
                break
            flat = self.matrix([[x.mid()] for x in read["causal_flat"].entries()])
            need(norm(flat) < self.q(1, 32), "A_CI_PC proposal leaves root ball")
        else:
            raise RuntimeError("A_CI_PC root proposal iteration limit")
        actual_rows = self.rows(C, W)
        read = self.read(C, W, self.composite_geometry(flat, Z), actual_rows)
        residual = norm(read["causal_flat"] - flat)
        error = (residual / (1 - self.root_q)).upper()
        need(norm(flat) + error < self.q(1, 32), "A_CI_PC enclosure leaves root ball")
        enclosed = self.matrix(
            [[self.scalar(x.fmpq(), error.fmpq())] for x in flat.entries()]
        )
        H = self.composite_geometry(enclosed, Z)
        selected = self.read(C, W, H, actual_rows)
        coefficient = self.scalar(
            sum((self.rational(x, 8)) ** 2 for row in self.overlap for x in row)
        ).sqrt()
        joint = coefficient * (2 * norm(flat) * residual + residual**2)
        source = self.source(enclosed)
        need(frobenius(source) < self.q(1, 64), "composite selected source envelope")
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
            "_Z": Z,
            "source": source,
        }

    def step(self, C, L, Z):
        read = self.root(C, L, Z)
        C1, L1, Z1 = self.advance(C, L, Z, read)
        return dict(**read, after=C1, logW_after=L1, carrier_after=Z1)

    def flat_partials(self, C, W, Z, flat, rows=None):
        H = self.composite_geometry(flat, Z)
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

    def jacobian(self, C, L, Z, root=None):
        root = self.root(C, L, Z) if root is None else root
        need(
            C is root["_C"] and L is root["_L"] and Z is root["_Z"],
            "full composite derivative subject",
        )
        W = root["_W"]
        nx, nz = self.n + self.m, len(self.carrier_pairs)
        d = nx + nz
        dC = self.matrix([[int(i == j) for j in range(d)] for i in range(self.n)])
        dL = self.matrix(
            [[int(self.n + i == j) for j in range(d)] for i in range(self.m)]
        )
        dW = self.diag(W) * dL
        dHs = [self.matrix(self.m, self.m) for _ in range(d)]
        for k, (i, j) in enumerate(self.carrier_pairs):
            dHs[nx + k][i, j] = dHs[nx + k][j, i] = (
                self.q(1, 2) if i == j else 1 / (2 * self.scalar(2).sqrt())
            )
        selected, H, Ff, Jf = self.flat_partials(C, W, Z, root["flat"], self.rows(C, W))
        need(norm(Ff) < self.root_q, "composite implicit derivative root bound")
        Jx, qx = self.read_derivative(
            C, W, H, selected, dC, dW, dHs, self.rows(C, W, dC, dW)
        )
        rhs = (self.diag(selected["q"]) * Jx + self.diag(selected["current"]) * qx) / 2
        rhs -= self.matrix(
            [
                [
                    sum(
                        dHs[k][i, j] * selected["causal_flat"][j, 0]
                        for j in range(self.m)
                    )
                    for k in range(d)
                ]
                for i in range(self.m)
            ]
        )
        Fx = H.solve(rhs)
        # One implicit multiple-RHS solve includes every direct C/W/Z column.
        df = (self.I - Ff).solve(Fx)
        dJ = Jx + Jf * df
        flat = root["flat"]
        dS = self.matrix(
            [
                [
                    (1 if i == j else self.scalar(2).sqrt())
                    * self.overlap[i][j]
                    / 4
                    * (flat[i, 0] * df[j, k] + flat[j, 0] * df[i, k])
                    for k in range(d)
                ]
                for i, j in self.carrier_pairs
            ]
        )
        ca = C - 32 * self.B * selected["current"]
        dca = dC - 32 * self.B * dJ
        _, de = self.exponent(ca, W, selected["current"], None, dca, dW, dJ)
        dl = self.decay * dL + (1 - self.decay) * de
        dz = (1 - self.decay) * dS
        for i in range(nz):
            dz[i, nx + i] += self.decay
        return self.matrix(dca.tolist() + dl.tolist() + dz.tolist())
