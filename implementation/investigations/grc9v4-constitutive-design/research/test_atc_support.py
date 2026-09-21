"""Focused local-research checks, including an independent expanded oracle."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
import math
import sys
import unittest

import atc_support as model

COEFFICIENTS = tuple(map(F, ('-405/32', '657/16', '-1647/32', '497/16', '-9', '1')))


def oracle(graph, C):
    """No use of model polynomial, component traversal or field assembly."""
    B = tuple(tuple(int(v == e.tail_node_id)-int(v == e.head_node_id)
                    for e in graph.oriented_edges) for v in graph.live_node_ids)
    L = tuple(tuple(sum(a*b for a, b in zip(x, y, strict=True)) for y in B) for x in B)
    c = tuple(map(F, C))
    p = tuple(sum((a*x**i for i, a in enumerate(COEFFICIENTS)), F()) for x in c)
    # Independent adjacency transitive closure, also covers disconnected controls.
    adjacency = [{i} | {j for j in range(len(C)) if L[i][j] != 0} for i in range(len(C))]
    for _ in C:
        adjacency = [set().union(*(adjacency[j] for j in s)) for s in adjacency]
    phi = tuple(F(1, 1024)*sum((a*x for a, x in zip(row, c, strict=True)), F())
                -p[i]+sum((p[j] for j in sorted(adjacency[i])), F())/len(adjacency[i])
                for i, row in enumerate(L))
    Phi = tuple(map(float, phi))
    J = tuple(float(-F(1, 4)*sum((F(B[i][e])*F(Phi[i]) for i in range(len(C))), F()))
              for e in range(len(graph.oriented_edges)))
    f = tuple(-sum((F(b)*F(j) for b, j in zip(row, J, strict=True)), F()) for row in B)
    return Phi, J, f


def source():
    eps = 2**-12
    return model.admit(model.State(model.SOURCE_GRAPH, (1., 3., 1.), (1.+eps, 3.-2*eps, 1.+eps)))


class SupportTests(unittest.TestCase):
    def test_binding_and_distinct_identity(self):
        binding = model.load_binding()
        self.assertEqual(binding['symbolic_id'], 'research_atc_sup_mw_site_derivative_v1')
        self.assertNotEqual(binding['symbolic_id'], 'quadratic_site_potential_zero_derivative_v1')

    def test_graph_domain(self):
        bad = (
            ((), ()),
            (tuple(str(i) for i in range(17)), ()),
            (('a', 'a'), ()),
            (('a', 'b'), (model.Edge('x', 'a', 'a'),)),
            (('a', 'b'), (model.Edge('x', 'a', 'q'),)),
            (('a', 'b'), (model.Edge('x', 'a', 'b'), model.Edge('y', 'b', 'a'))),
            (('a', 'b', 'c'), (model.Edge('x', 'a', 'b'), model.Edge('x', 'b', 'c'))),
            (('a', 'b', 'c', 'd'), tuple(model.Edge(v, 'a', v) for v in ('b', 'c', 'd'))),
            (('a', 'b'), (model.Edge('x', 'a', 'b'),)*33),
        )
        for vertices, edges in bad:
            with self.subTest(vertices=vertices, edges=len(edges)), self.assertRaises(model.ResearchDomainError):
                model.Graph(vertices, edges)

    def test_invalid_resources(self):
        for bad in (-1., float('nan'), float('inf'), -float('inf'), True, 1, '1'):
            with self.subTest(value=str(bad)), self.assertRaises(model.ResearchDomainError):
                model.read(model.SOURCE_GRAPH, (bad, 3., 1.))
        with self.assertRaises(model.ResearchDomainError):
            model.read(model.SOURCE_GRAPH, (1., 3.))

    def test_components_and_nonfinite_output(self):
        graph = model.Graph(('a', 'b', 'c', 'd', 'z'),
            (model.Edge('ab', 'a', 'b'), model.Edge('cd', 'c', 'd')))
        C = (1.125, 1.125, 2.5, 2.5, .125)
        result = model.read(graph, C)
        self.assertEqual(result.Phi, (0.,)*5)
        self.assertEqual((result.Phi, result.J, result.f), oracle(graph, C))
        # Exact cancellation is permitted BEFORE the consumed-output rounding.
        huge = sys.float_info.max
        self.assertEqual(model.read(model.SOURCE_GRAPH, (huge,)*3).Phi, (0.,)*3)
        with self.assertRaises(model.ResearchDomainError):
            model.read(model.SOURCE_GRAPH, (huge, 1., 1.))
        tiny = float.fromhex('0x0.0000000000001p-1022')
        result = model.read(model.SOURCE_GRAPH, (-0., tiny, 1.))
        self.assertTrue(all(math.isfinite(x) for x in result.Phi+result.J))

    def test_off_root_current_and_initializer_oracle(self):
        for graph, c in ((model.SOURCE_GRAPH, source().reset_C),
                         (model.TARGET_GRAPH, (1.000244140625, 1.000244140625, 1.499755859375, 1.499755859375))):
            expected = oracle(graph, c)
            result = model.read(graph, c)
            self.assertEqual((result.Phi, result.J, result.f), expected)
            for role in ('current', 'reset'):
                record = model.initialize(graph, c, role)
                self.assertEqual(record['payload']['derived']['Phi_base'], expected[0])
                self.assertEqual(record['payload']['derived']['J_ref'], expected[1])
                model.check_initialization(record, graph, c, role)
                # Site omission is detectable even though W remains all-one.
                zero_site_phi = tuple(float(F(1, 1024)*sum(
                    ((F(c[i])-F(c[graph.live_node_ids.index(
                        e.head_node_id if e.tail_node_id == v else e.tail_node_id)]))
                     for e in graph.oriented_edges if v in (e.tail_node_id, e.head_node_id)), F()))
                    for i, v in enumerate(graph.live_node_ids))
                self.assertNotEqual(expected[0], zero_site_phi)
                omitted = deepcopy(record)
                omitted['payload']['derived']['Phi_base'] = zero_site_phi
                omitted['payload']['derived']['J_ref'] = tuple(float(-F(1,4)*(
                    F(zero_site_phi[graph.live_node_ids.index(e.tail_node_id)])-
                    F(zero_site_phi[graph.live_node_ids.index(e.head_node_id)])))
                    for e in graph.oriented_edges)
                omitted['research_construction_digest'] = model.digest(omitted['payload'])
                with self.assertRaises(model.ResearchDomainError):
                    model.check_initialization(omitted, graph, c, role)
                for replacement in (None, {}):
                    changed = deepcopy(record)
                    changed['payload']['derived'] = replacement
                    changed['research_construction_digest'] = model.digest(changed['payload'])
                    with self.assertRaises(model.ResearchDomainError):
                        model.check_initialization(changed, graph, c, role)

    def test_reset_and_input_preservation(self):
        before = source()
        after = model.advance(before)
        self.assertEqual(before.C, (1., 3., 1.))
        self.assertEqual(after.reset_C, before.reset_C)
        self.assertEqual(model.reset(after).C, before.reset_C)
        with self.assertRaises(model.ResearchDomainError):
            replace(before, reset_C=(-1., 3., 3.))
        with self.assertRaises(model.ResearchDomainError):
            replace(before, reset_C=(1., 2., 1.))
        self.assertEqual(before.C, (1., 3., 1.))

    def test_orientation_and_order_covariance(self):
        graph = model.Graph(('c', 'b', 'a'),
            (model.Edge('bc', 'c', 'b'), model.Edge('ab', 'b', 'a')))
        C = (1.125, 2.5, 1.375)
        original = model.read(model.SOURCE_GRAPH, C)
        changed = model.read(graph, tuple(reversed(C)))
        self.assertEqual(changed.Phi, tuple(reversed(original.Phi)))
        self.assertEqual(changed.J, tuple(-x for x in reversed(original.J)))
        self.assertEqual(changed.f, tuple(reversed(original.f)))

    def test_fission_scope(self):
        choice = dict(vertex='b', blocks=[[['ab', 'head']], [['bc', 'tail']]], shares=['1/2', '1/2'])
        target, initialization = model.fixed_fission(source(), choice)
        self.assertEqual(target.C, (1., 1., 1.5, 1.5))
        self.assertNotEqual(target.C, target.reset_C)
        self.assertEqual(set(initialization), {'current', 'reset'})
        with self.assertRaises(model.ResearchDomainError):
            model.fixed_fission(model.advance(source()), choice)


if __name__ == '__main__':
    unittest.main()
