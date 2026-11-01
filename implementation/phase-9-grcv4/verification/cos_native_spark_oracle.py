"""Verification-only C_OS equations and geometric reachability.

No production, research evaluator, allocator, or classifier imports. Callers
capture ordered graph/resources before public execution. Exact FLINT arithmetic
and a separately assembled Arb evaluation share only the printed equations.
"""

from flint import arb_mat
from flint import fmpq as Q
from flint import fmpq_mat as M


def matrix(rows):
    return M([[Q(str(x)) for x in row] for row in rows])


def vector(values):
    return matrix([[x] for x in values])


def incidence(graph):
    nodes, edges = graph["live_node_ids"], graph["edges"]
    return M(
        [
            [
                int(e["tail"]["node_id"] == n) - int(e["head"]["node_id"] == n)
                for e in edges
            ]
            for n in nodes
        ]
    )


class Equations:
    def __init__(self, graph, *, outward=False):
        self.M = arb_mat if outward else M
        B = incidence(graph)
        self.B = self.M(B)
        self.I = self.M(
            [[int(i == j) for j in range(B.ncols())] for i in range(B.ncols())]
        )
        absolute = self.M(
            [[abs(B[i, j]) for j in range(B.ncols())] for i in range(B.nrows())]
        )
        self.L = self.B.transpose() * self.B
        self.O = absolute.transpose() * absolute

    def read(self, C, H):
        site = self.M([[(C[i, 0] - 2) ** 3 - (C[i, 0] - 2)] for i in range(C.nrows())])
        phi = self.B * H * self.B.transpose() * C / 64 - site
        j0 = -self.B.transpose() * phi / 1024
        y = (3 * self.I / 4 + H * self.L).inv() * j0
        return j0 + y / 4, H.inv() * y / 2

    def geometry(self, flat):
        return self.I + self.M(
            [
                [
                    flat[i, 0] * self.O[i, j] * flat[j, 0] / 8
                    for j in range(flat.nrows())
                ]
                for i in range(flat.nrows())
            ]
        )

    def step(self, values):
        C = self.M(vector(values))
        jp, fp = self.read(C, self.I)
        H = self.geometry(fp)
        jc, fc = self.read(C, H)
        return {
            "C": C,
            "predictor_current": jp,
            "predictor_flat": fp,
            "H": H,
            "corrector_current": jc,
            "corrector_flat": fc,
            "split": H - self.geometry(fc),
            "after": C - 32 * self.B * jc,
        }


def contains(enclosure, exact):
    return (enclosure.nrows(), enclosure.ncols()) == (
        exact.nrows(),
        exact.ncols(),
    ) and all(
        ball.lower().fmpq() <= q <= ball.upper().fmpq()
        for ball, q in zip(enclosure.entries(), exact.entries(), strict=True)
    )


def nullspace(A):
    reduced, rank = A.rref()
    pivots = [next(j for j in range(A.ncols()) if reduced[i, j]) for i in range(rank)]
    basis = []
    for free in range(A.ncols()):
        if free not in pivots:
            v = M(A.ncols(), 1)
            v[free, 0] = 1
            for i, pivot in enumerate(pivots):
                v[pivot, 0] = -reduced[i, free]
            basis.append(v)
    return basis


def infinity(A):
    return max(sum(abs(A[i, j]) for j in range(A.ncols())) for i in range(A.nrows()))


def classify(graph, values, policy):
    """Exhaustive reachability, including unqualified terminals, then domains."""
    nodes = graph["live_node_ids"]
    C = dict(zip(nodes, map(Q, values), strict=True))
    sign = policy["landscape_sign"]
    adjacency = {n: set() for n in nodes}
    terms = {n: [[], [], []] for n in nodes}
    for edge in graph["edges"]:
        a, b = edge["tail"], edge["head"]
        for here, there in ((a, b), (b, a)):
            x, y = here["node_id"], there["node_id"]
            adjacency[x].add(y)
            terms[x][(here["port"] - 1) // 3].append(C[y] - C[x])
    down = {x: {y for y in adjacency[x] if sign * (C[y] - C[x]) < 0} for x in nodes}
    terminals = {}
    for start in nodes:
        pending, seen, ends = [start], set(), set()
        while pending:
            x = pending.pop()
            if x in seen:
                continue
            seen.add(x)
            if down[x]:
                pending.extend(down[x])
            else:
                ends.add(x)
        terminals[start] = tuple(x for x in nodes if x in ends)
    rows, anchors = [], set()
    for x in nodes:
        means = [sum(row, Q(0)) / len(row) if row else Q(0) for row in terms[x]]
        squared, minimum = sum(g * g for g in means), min(sign * g for g in means)
        seed = squared < Q(policy["epsilon_gradient"]) ** 2 and minimum > Q(
            policy["epsilon_Hessian"]
        )
        anchor = (
            seed
            and bool(adjacency[x])
            and C[x] > Q(policy["minimum_resource"])
            and all(sign * (C[y] - C[x]) > Q(policy["contrast"]) for y in adjacency[x])
        )
        rows.append(
            {
                "node_id": x,
                "gradient": list(map(str, means)),
                "gradient_squared": str(squared),
                "minimum_signed_gradient": str(minimum),
                "seed": seed,
                "anchor": anchor,
                "evaluation_error": "0",
            }
        )
        if anchor:
            anchors.add(x)
    domains = [
        (a, tuple(x for x in nodes if terminals[x] == (a,)))
        for a in nodes
        if a in anchors
    ]
    return (
        tuple((a, members) for a, members in domains if len(members) > 1),
        tuple(terminals.items()),
        rows,
    )
