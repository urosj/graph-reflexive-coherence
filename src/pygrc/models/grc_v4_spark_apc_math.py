"""Full A_PC C/logW/Z equations and all signed-star derivatives."""

from .grc_v4_spark_aos_math import AOSMath
from .grc_v4_spark_carrier import carrier_pairs
from .grc_v4_spark_cpc import need


class APCMath(AOSMath):
    def __init__(self, graph):
        super().__init__(graph)
        self.carrier_pairs = carrier_pairs(graph)

    def source(self, flat):
        S = self.matrix(self.m, self.m)
        for i, j in self.carrier_pairs:
            S[i, j] = S[j, i] = self.overlap[i][j] * flat[i, 0] * flat[j, 0] / 4
        return S

    def pc_read(self, C, L, Z, W=None):
        W = self.exp(L) if W is None else W
        H = self.I + Z / 2
        selected = self.read(C, W, H)
        return {
            "geometry": H,
            "selected": selected,
            "source": self.source(selected["causal_flat"]),
            "_C": C,
            "_L": L,
            "_W": W,
            "_Z": Z,
        }

    def advance(self, C, L, Z, read):
        need(
            C is read["_C"] and L is read["_L"] and Z is read["_Z"],
            "complete A_PC read subject changed",
        )
        J = read["selected"]["current"]
        after = C - 32 * self.B * J
        exponent, _ = self.exponent(after, read["_W"], J)
        return (
            after,
            self.decay * L + (1 - self.decay) * exponent,
            self.decay * Z + (1 - self.decay) * read["source"],
        )

    def step(self, C, L, Z):
        read = self.pc_read(C, L, Z)
        C1, L1, Z1 = self.advance(C, L, Z, read)
        return dict(**read, after=C1, logW_after=L1, carrier_after=Z1)

    def carrier_coordinates(self, Z):
        return self.matrix(
            [
                [Z[i, j] * (1 if i == j else self.scalar(2).sqrt())]
                for i, j in self.carrier_pairs
            ]
        )

    def jacobian(self, C, L, Z):
        """Physical C/logW columns and Frobenius-orthonormal carrier columns."""
        nx, nz = self.n + self.m, len(self.carrier_pairs)
        d = nx + nz
        W = self.exp(L)
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
        read = self.pc_read(C, L, Z, W)
        selected, H = read["selected"], read["geometry"]
        dJ, dq = self.read_derivative(
            C, W, H, selected, dC, dW, dHs, self.rows(C, W, dC, dW)
        )
        flat = selected["causal_flat"]
        rhs = (self.diag(selected["q"]) * dJ + self.diag(selected["current"]) * dq) / 2
        rhs -= self.matrix(
            [
                [
                    sum(dHs[k][i, j] * flat[j, 0] for j in range(self.m))
                    for k in range(d)
                ]
                for i in range(self.m)
            ]
        )
        # One multiple-RHS inverse derivative; no solve per carrier coordinate.
        df = H.solve(rhs)
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
