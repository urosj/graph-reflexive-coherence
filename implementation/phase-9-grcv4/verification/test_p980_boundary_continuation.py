"""Independent exact reference-continuation research; no production ATC.

One declared recipe covers the 16 frozen D30/D31/D45/D52 role layouts, not
their frozen numerical identities. Fraction arithmetic implements C+=C+dt L^2 C
for the reference/no-feedback reduction. No production current/step evaluator
provides expected results. Enabled-realization and represented-number lifts
remain separate obligations.
"""
from fractions import Fraction as Q
import json
from pathlib import Path
import unittest

from test_p980_feasibility import laplacian

ROOT = Path(__file__).resolve().parents[3]
DT = Q(1, 4096)
OUTSIDE_OFFSET = Q(1, 64)
HORIZON = 10
CUTOFF = Q(1, 512)
RESOURCE_MARGIN = Q(1, 8192)
RATE_ERROR_BUDGET = Q(1, 96)


def rate(edges, values):
    weights = {e["edge_id"]: 1 for e in edges}
    return laplacian(edges, weights, laplacian(edges, weights, values))


def step(edges, values, dt=DT):
    velocity = rate(edges, values)
    return {n: c + dt * velocity[n] for n, c in values.items()}


def solve(matrix, rhs):
    """Small exact elimination, independent of production inverse code."""
    rows = [[Q(x) for x in row] + [Q(b)] for row, b in zip(matrix, rhs, strict=True)]
    n = len(rows)
    for col in range(n):
        pivot = next(i for i in range(col, n) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [x / divisor for x in rows[col]]
        for i in range(n):
            if i != col:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[col], strict=True)]
    return [row[-1] for row in rows]


def preimage(edges, values):
    nodes = tuple(values)
    columns = [step(edges, {n: Q(n == k) for n in nodes}) for k in nodes]
    matrix = [[col[n] for col in columns] for n in nodes]
    result = solve(matrix, list(values.values()))
    return dict(zip(nodes, result, strict=True))


def normalized_target(vector):
    """Reuse role topology only; never reuse a frozen event/model identity."""
    target = vector["expected"]
    prefix = target["event_id"] + "/"

    def role(value):
        return value.removeprefix(prefix)

    edges = [{"edge_id": role(e["edge_id"]),
              "tail": {"node_id": role(e["tail"]["node_id"]), "port": e["tail"]["port"]},
              "head": {"node_id": role(e["head"]["node_id"]), "port": e["head"]["port"]}}
             for e in target["target_edges"]]
    return edges, tuple(role(n) for n in target["target_live_node_ids"])


def resources(nodes, source_value):
    return {n: source_value + OUTSIDE_OFFSET if n.startswith("outside-")
            else source_value / 3 if n.startswith("satellite/") else Q(0)
            for n in nodes}


class BoundaryContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vectors = json.loads((ROOT / "specs/grc-v4-conformance-vectors.json").read_text())
        cls.layouts = [r for r in cls.vectors["grc9_expansion_vectors"]
                       if r["fixture_id"].startswith("G9-EXPAND-D")]
        cls.source = cls.vectors["port_graph_envelope_vectors"][0]["payload"]

    def test_source_is_reached_by_a_positive_ordinary_reference_step(self):
        for source_value in (Q(3), Q(2)):
            desired = {n: source_value if n == "source-s" else source_value + OUTSIDE_OFFSET
                       for n in self.source["live_node_ids"]}
            before = preimage(self.source["edges"], desired)
            self.assertTrue(all(c > 0 for c in before.values()))
            self.assertEqual(before["source-s"],
                             source_value + 90 * DT * OUTSIDE_OFFSET / (1 + 100 * DT))
            self.assertEqual(step(self.source["edges"], before), desired)
            self.assertEqual(sum(before.values()), sum(desired.values()))
            ports = {}
            for e in self.source["edges"]:
                end, other = ((e["tail"], e["head"]) if e["tail"]["node_id"] == "source-s"
                              else (e["head"], e["tail"]))
                self.assertEqual(end["node_id"], "source-s")
                self.assertNotIn(end["port"], ports)
                ports[end["port"]] = desired[other["node_id"]] - desired["source-s"]
            self.assertEqual(set(ports), set(range(1, 10)))
            rows = [sum(ports[p] for p in range(3*a+1, 3*a+4)) / 3 for a in range(3)]
            self.assertEqual(rows, [OUTSIDE_OFFSET] * 3)
            # s_H=-1, epsilon_grad=1/2, epsilon_spark=0: a candidate,
            # not a completed spark or autonomous expansion request.
            self.assertLess(sum(g*g for g in rows), Q(1, 2)**2)
            self.assertLess(min(-g for g in rows), 0)

    def test_graph_and_perturbation_bound_hypotheses(self):
        for vector in self.layouts:
            edges, nodes = normalized_target(vector)
            adjacency = {n: set() for n in nodes}
            for e in edges:
                u, v = e["tail"]["node_id"], e["head"]["node_id"]
                self.assertNotEqual(u, v)
                self.assertNotIn(v, adjacency[u])
                adjacency[u].add(v)
                adjacency[v].add(u)
            reached = {nodes[0]}
            for _ in nodes:
                reached |= {v for u in tuple(reached) for v in adjacency[u]}
            self.assertEqual(reached, set(nodes))
            self.assertEqual(len(edges), len(nodes)-1)
            self.assertLessEqual(len(nodes), 17)
            self.assertLessEqual(max(map(len, adjacency.values())), 5)
            # Strict constant-sector gap even for ||H1-I||_2 <= 1/2.
            self.assertLess(CUTOFF, Q(1, len(nodes) * (len(nodes)-1)))
        # ||L||_inf <= 2*d_max <= 10 on each target.
        amplification = sum((1 + 100*DT)**j for j in range(HORIZON))
        self.assertLess(amplification, 12)
        self.assertLess(DT * RATE_ERROR_BUDGET * amplification, RESOURCE_MARGIN / 4)

    def test_every_layout_and_role_has_strict_boundary_inflow_and_ten_steps(self):
        self.assertEqual(len(self.layouts), 16)
        self.assertEqual({r["request"]["target_effective_degree"] for r in self.layouts},
                         {30, 31, 45, 52})
        observed_minimum = Q(10)
        for vector in self.layouts:
            edges, nodes = normalized_target(vector)
            # Connected unit-weight graph: elementary mean-zero bound
            # lambda_2 >= 2/(N*(N-1)), proved in the note.
            self.assertLess(CUTOFF, Q(2, len(nodes) * (len(nodes) - 1)))
            for role, source_value in (("current", Q(3)), ("reset", Q(2))):
                with self.subTest(vector=vector["fixture_id"], role=role):
                    values = resources(nodes, source_value)
                    velocity = rate(edges, values)
                    charge = 10 * source_value + 9 * OUTSIDE_OFFSET
                    self.assertEqual(sum(values.values()), charge)
                    zero_rates = [velocity[n] for n, c in values.items() if c == 0]
                    self.assertTrue(zero_rates)
                    self.assertGreaterEqual(min(zero_rates), Q(2, 3))
                    for _ in range(HORIZON):
                        values = step(edges, values)
                        self.assertTrue(all(c > 0 for c in values.values()))
                        self.assertGreaterEqual(min(values.values()), RESOURCE_MARGIN)
                        observed_minimum = min(observed_minimum, *values.values())
                        self.assertEqual(sum(values.values()), charge)
        self.assertEqual(observed_minimum, Q(1, 6144))

    def test_resource_map_and_reference_trajectory_are_covariant(self):
        for vector in self.layouts:
            edges, nodes = normalized_target(vector)
            values = resources(nodes, Q(3))
            expected = step(edges, values)
            reversed_edges = [dict(e, tail=e["head"], head=e["tail"]) for e in reversed(edges)]
            self.assertEqual(step(reversed_edges, values), expected)
            names = {n: f"v-{len(nodes)-i}" for i, n in enumerate(nodes)}
            moved = [dict(e, tail=dict(e["tail"], node_id=names[e["tail"]["node_id"]]),
                          head=dict(e["head"], node_id=names[e["head"]["node_id"]])) for e in edges]
            self.assertEqual(step(moved, {names[n]: c for n, c in values.items()}),
                             {names[n]: c for n, c in expected.items()})

    def test_inward_target_has_a_signed_auxiliary_preimage(self):
        edges, nodes = normalized_target(self.layouts[0])
        target = resources(nodes, Q(3))
        ghost = preimage(edges, target)
        self.assertEqual(ghost["core"], Q(-1584651, 1083714112))
        self.assertLess(ghost["core"], 0)
        self.assertEqual(step(edges, ghost), target)
        self.assertEqual(sum(ghost.values()), sum(target.values()))
        # Clipping the auxiliary predecessor is not an inverse and cannot
        # be slipped into the graph transform as a domain repair.
        clipped = {n: max(Q(0), c) for n, c in ghost.items()}
        self.assertNotEqual(step(edges, clipped), target)


if __name__ == "__main__":
    unittest.main()
