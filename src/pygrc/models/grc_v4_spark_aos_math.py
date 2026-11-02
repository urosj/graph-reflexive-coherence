"""Full A_OS equations and analytic C/logW derivative for native certification.

Both OS reads and the final-C writer use incoming W and fixed port rows.
Every interval operation runs inside the caller's locked Arb precision scope.
"""

from .grc_v4_codec import canonical_json_bytes
from .grc_v4_exact import _flint_module
from .grc_v4_spark_conductance import fixed_rows
from .grc_v4_spark_cos import _matrix, _reference_facts
from .grc_v4_spark_cpc import decay, need
from .grc_v4_spark_cpc import frobenius as norm_upper


class AOSMath:
    def __init__(self, graph):
        f = _flint_module()
        self.graph = graph
        self.nodes, self.edge_ids = graph.live_node_ids, graph.live_edge_ids
        facts = _reference_facts(canonical_json_bytes(graph.to_payload()))
        self.B, self.I = f.arb_mat(_matrix(facts[0])), f.arb_mat(_matrix(facts[1]))
        self.Bt = self.B.transpose()
        self.pairs = tuple(
            (graph.node_index(e.tail_node_id), graph.node_index(e.head_node_id))
            for e in graph.oriented_edges
        )
        self.terms = fixed_rows(graph)
        self.overlap = tuple(tuple(int(x) for x in row) for row in facts[3])
        self.n, self.m = len(self.nodes), len(self.edge_ids)
        self.decay = decay()
        self.floor_log = -f.arb(2).log()

    @staticmethod
    def matrix(*args):
        return _flint_module().arb_mat(*args)

    @staticmethod
    def scalar(*args):
        return _flint_module().arb(*args)

    @staticmethod
    def rational(*args):
        return _flint_module().fmpq(*args)

    def q(self, n, d=1):
        return self.scalar(self.rational(n, d))

    def vector(self, values):
        return self.matrix(
            [[self.scalar(self.rational(values[n]))] for n in self.nodes]
        )

    def diag(self, v):
        return self.matrix(
            [
                [v[i, 0] if i == j else 0 for j in range(v.nrows())]
                for i in range(v.nrows())
            ]
        )

    def exp(self, L):
        return self.matrix([[L[i, 0].exp()] for i in range(self.m)])

    def site(self, C):
        return self.matrix(
            [
                [(C[i, 0] - 2) * (C[i, 0] - 2) * (C[i, 0] - 2) - (C[i, 0] - 2)]
                for i in range(self.n)
            ]
        )

    def rows(self, C, W, dC=None, dW=None):
        values = []
        derivatives = []
        d = dC.ncols() if dC is not None else 0
        for i, terms in enumerate(self.terms):
            vr = []
            dr = []
            for row in terms:
                den = sum((W[k, 0] for k, j in row), self.scalar(0))
                if not row:
                    v = self.scalar(0)
                    dv = [self.scalar(0)] * d
                else:
                    need(den > 0, "positive fixed-row denominator")
                    v = (
                        sum(
                            (W[k, 0] * (C[j, 0] - C[i, 0]) for k, j in row),
                            self.scalar(0),
                        )
                        / den
                    )
                    dv = [
                        sum(
                            (
                                dW[k, l] * (C[j, 0] - C[i, 0] - v)
                                + W[k, 0] * (dC[j, l] - dC[i, l])
                                for k, j in row
                            ),
                            self.scalar(0),
                        )
                        / den
                        for l in range(d)
                    ]
                vr.append(v)
                dr.append(dv)
            values.append(vr)
            derivatives.append(dr)
        return values, derivatives

    def exponent(self, C, W, J, rows=None, dC=None, dW=None, dJ=None):
        rv, rd = self.rows(C, W, dC, dW) if rows is None else rows
        out = []
        der = []
        d = dC.ncols() if dC is not None else 0
        for k, (i, j) in enumerate(self.pairs):
            v = (
                -(
                    C[i, 0]
                    + C[j, 0]
                    + sum(
                        (rv[i][r] - rv[j][r]) * (rv[i][r] - rv[j][r]) for r in range(3)
                    )
                    + J[k, 0] * J[k, 0]
                )
                / 65536
            )
            # This bounded certificate uses the smooth, strictly floor-inactive branch.
            need(v > self.floor_log, "conductance floor not strictly inactive")
            out.append([v])
            der.append(
                [
                    -(
                        dC[i, l]
                        + dC[j, l]
                        + sum(
                            2 * (rv[i][r] - rv[j][r]) * (rd[i][r][l] - rd[j][r][l])
                            for r in range(3)
                        )
                        + 2 * J[k, 0] * dJ[k, l]
                    )
                    / 65536
                    for l in range(d)
                ]
            )
        return self.matrix(out), self.matrix(der) if d else None

    def read(self, C, W, H, rows=None):

        phi = (
            self.B * self.diag(W) * self.Bt * C / 64
            - self.site(C)
            + self.B * (H - self.I) * self.Bt * C / 64
        )
        j0 = -self.diag(W) * self.Bt * phi / 1024
        exponent, _ = self.exponent(C, W, j0, rows)
        G = self.exp(exponent)
        q = self.matrix(
            [[(W[k, 0] - G[k, 0]) / (W[k, 0] + G[k, 0])] for k in range(self.m)]
        )
        den = [1 - q[k, 0] / 4 for k in range(self.m)]
        need(all(x > self.q(3, 4) for x in den), "positive physical closure")
        J = self.matrix([[j0[k, 0] / den[k]] for k in range(self.m)])
        causal = self.matrix([[q[k, 0] * J[k, 0] / 2] for k in range(self.m)])
        flat = causal if H is self.I else H.solve(causal)
        return {
            "potential": phi,
            "baseline": j0,
            "drive": G,
            "q": q,
            "current": J,
            "causal_flat": flat,
        }

    def geometry(self, f):
        return self.I + self.matrix(
            [
                [self.overlap[i][j] * f[i, 0] * f[j, 0] / 8 for j in range(self.m)]
                for i in range(self.m)
            ]
        )

    def os_read(self, C, L, W=None):
        W = self.exp(L) if W is None else W
        need(all(x > 0 for x in W.entries()), "positive conductance")
        rows = self.rows(C, W)
        pred = self.read(C, W, self.I, rows)
        H = self.geometry(pred["causal_flat"])
        corr = self.read(C, W, H, rows)
        defect = norm_upper(H - self.geometry(corr["causal_flat"]))
        # The owning kernel checks the exact declared binary64 tolerance.
        need(defect < self.q(1, 10**11), "OS split tolerance exceeded")
        return {
            "predictor": pred,
            "geometry": H,
            "corrector": corr,
            "split_upper": defect,
            "_C": C,
            "_L": L,
            "_W": W,
        }

    def advance(self, C, L, read):
        need(C is read["_C"] and L is read["_L"], "read subject changed")
        W = read["_W"]
        J = read["corrector"]["current"]
        after = C - 32 * self.B * J
        exponent, _ = self.exponent(after, W, J)

        return after, self.decay * L + (1 - self.decay) * exponent

    def step(self, C, L):
        read = self.os_read(C, L)
        after, ln = self.advance(C, L, read)
        return dict(**read, after=after, logW_after=ln)

    def read_derivative(self, C, W, H, read, dC, dW, dHs, rows):
        d = dC.ncols()
        dc = self.Bt * C
        phi = read["potential"]
        j0 = read["baseline"]
        G = read["drive"]
        q = read["q"]
        extra = self.matrix(
            [
                [sum(dHs[l][i, j] * dc[j, 0] for j in range(self.m)) for l in range(d)]
                for i in range(self.m)
            ]
        )
        curvature = self.diag(
            self.matrix([[3 * (C[i, 0] - 2) ** 2 - 1] for i in range(self.n)])
        )
        dp = (
            self.B
            * (
                self.diag(W) * self.Bt * dC
                + self.diag(dc) * dW
                + (H - self.I) * self.Bt * dC
                + extra
            )
            / 64
            - curvature * dC
        )
        dj = -((self.diag(W) * self.Bt * dp) + (self.diag(self.Bt * phi) * dW)) / 1024
        _, de = self.exponent(C, W, j0, rows, dC, dW, dj)
        dg = self.diag(G) * de
        dq = self.matrix(
            [
                [
                    2
                    * (G[k, 0] * dW[k, l] - W[k, 0] * dg[k, l])
                    / (W[k, 0] + G[k, 0]) ** 2
                    for l in range(d)
                ]
                for k in range(self.m)
            ]
        )
        dJ = self.matrix(
            [
                [
                    dj[k, l] / (1 - q[k, 0] / 4)
                    + j0[k, 0] * dq[k, l] / (4 * (1 - q[k, 0] / 4) ** 2)
                    for l in range(d)
                ]
                for k in range(self.m)
            ]
        )
        return dJ, dq

    def jacobian(self, C, L):
        d = self.n + self.m
        W = self.exp(L)
        dC = self.matrix([[int(i == j) for j in range(d)] for i in range(self.n)])
        dL = self.matrix(
            [[int(self.n + i == j) for j in range(d)] for i in range(self.m)]
        )
        dW = self.diag(W) * dL
        rows = self.rows(C, W, dC, dW)
        s = self.os_read(C, L)
        p = s["predictor"]
        c = s["corrector"]
        zero = self.matrix(self.m, self.m)
        dj, dq = self.read_derivative(C, W, self.I, p, dC, dW, [zero] * d, rows)
        df = (self.diag(p["q"]) * dj + self.diag(p["current"]) * dq) / 2
        f = p["causal_flat"]
        dHs = [
            self.matrix(
                [
                    [
                        self.overlap[i][j]
                        * (df[i, l] * f[j, 0] + f[i, 0] * df[j, l])
                        / 8
                        for j in range(self.m)
                    ]
                    for i in range(self.m)
                ]
            )
            for l in range(d)
        ]
        dj, _ = self.read_derivative(C, W, s["geometry"], c, dC, dW, dHs, rows)
        ca = C - 32 * self.B * c["current"]
        dca = dC - 32 * self.B * dj
        _, de = self.exponent(ca, W, c["current"], None, dca, dW, dj)
        dl = self.decay * dL + (1 - self.decay) * de
        return self.matrix(dca.tolist() + dl.tolist())
