"""Exact fixture-scope reconciliation; no numerical proof rerun or admission."""
import copy
import unittest
from unittest.mock import patch

import test_p980_boundary_continuation as boundary
import test_p980_fixed_row_bounds as fixed
import test_p980_os_effect_witness as effect
import test_p980_os_numerical_feasibility as numerical
import test_p980_revised_realization_bounds as revised
import test_p980_rg2b_completion as rg


class ScopeBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        boundary.BoundaryContinuationTests.setUpClass()
        cls.layouts = boundary.BoundaryContinuationTests.layouts
        cls.source = boundary.BoundaryContinuationTests.source

    def test_exact_source_and_positive_phase_three_target_ports(self):
        layout = boundary.enabled_d52_layout(self.layouts)
        # Establish that pinning does not change any previously consumed input.
        self.assertEqual(layout, self.layouts[-1])
        source_edges = self.source['edges']
        self.assertEqual(self.source['live_node_ids'],
                         [f'outside-{i}' for i in range(1, 10)]+['source-s'])
        self.assertEqual([(e['edge_id'], e['tail'], e['head']) for e in source_edges],
                         [(f'old-{i}', dict(node_id='source-s', port=i),
                           dict(node_id=f'outside-{i}', port=i)) for i in range(1, 10)])
        edges, nodes = boundary.normalized_target(layout)
        expected = [(f'internal/{i}', 'core', f'satellite/{i}', port)
                    for i, port in enumerate((2, 6, 7), 1)]
        expected += [
            ('internal/extra/1/1', 'satellite/1', 'extra/1/1', 3),
            ('internal/extra/2/1', 'satellite/2', 'extra/2/1', 4),
            ('internal/extra/3/1', 'satellite/3', 'extra/3/1', 8),
            ('internal/extra/3/2', 'extra/3/1', 'extra/3/2', 9),
        ]
        expected += [(f'old-{i}', f'satellite/{(i-1)%3+1}', f'outside-{i}', i)
                     for i in range(1, 10)]
        self.assertEqual(edges, [dict(edge_id=e, tail=dict(node_id=u, port=p),
                                     head=dict(node_id=v, port=p)) for e, u, v, p in expected])
        self.assertEqual(set(nodes), {u for _, u, _, _ in expected} |
                         {v for _, _, v, _ in expected})
        self.assertEqual((len(nodes), len(edges)), (17, 16))
        module_size = len(nodes)-9
        self.assertEqual(module_size, max(4, (52-2+6)//7))
        self.assertEqual(9*module_size-2*(module_size-1), 58)
        occupied = [(end['node_id'], end['port']) for e in edges
                    for end in (e['tail'], e['head'])]
        self.assertEqual(len(occupied), len(set(occupied)))

    def test_selection_survives_reordering_and_rejects_ambiguous_scope(self):
        selected = boundary.enabled_d52_layout(self.layouts)
        self.assertIs(boundary.enabled_d52_layout(list(reversed(self.layouts))), selected)
        for layouts in ([], self.layouts[:-1], self.layouts+[selected]):
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                boundary.enabled_d52_layout(layouts)
        for field, value in (('module_chirality', -1), ('growth_phase', 2),
                             ('target_effective_degree', 45)):
            mutated = copy.deepcopy(selected)
            mutated['request'][field] = value
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                boundary.enabled_d52_layout([mutated])

    def test_actual_research_owners_consume_named_layout_after_reordering(self):
        selected = boundary.enabled_d52_layout(self.layouts)
        edges, nodes = boundary.normalized_target(selected)
        with patch.object(boundary.BoundaryContinuationTests, 'setUpClass'), \
                patch.object(boundary.BoundaryContinuationTests, 'layouts',
                             list(reversed(self.layouts))):
            fixed.FixedRowBoundTests.setUpClass()
            numerical.OSNumericalFeasibilityTests.setUpClass()
            effect.OSEffectWitnessTests.setUpClass()
            revised.RevisedRealizationBoundTests.setUpClass()
            rg.RGCompletionTests.setUpClass()
            self.assertIs(fixed.FixedRowBoundTests.d52, selected)
            self.assertIs(numerical.OSNumericalFeasibilityTests.vector_data, selected)
            self.assertIs(effect.OSEffectWitnessTests.layout, selected)
            for owner in (revised.RevisedRealizationBoundTests, rg.RGCompletionTests):
                self.assertEqual(owner.target.nodes, nodes)
                self.assertEqual(owner.target.edges, tuple(edges))


if __name__ == '__main__':
    unittest.main()
