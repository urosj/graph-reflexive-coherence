"""Actual G2 materializer, trusted projection and unchanged discovery scope."""

import unittest
import phase9_implementation_policy as p
import profile_g2_registry as registry
import verify_p977_a_rg2b_g2 as gate


class SurfaceTests(unittest.TestCase):
    def test_current_g2_checker_projects_only_the_pinned_proposal(self):
        roster=registry.registry(p.ROOT)
        bounded=roster['reconciliation_views']['a_rg2b_crossings']
        self.assertTrue(bounded['user_accepted'])
        checked=registry._checker(p.ROOT,'verify_p977_a_rg2b_g2')(bounded_acceptance=bounded)
        row=next(r for r in roster['records'] if r['complete_profile_id']==gate.NOMINATED)
        self.assertEqual(row['adapter'],'exact_profile_v1')
        self.assertEqual(row['state'],'proposed')
        self.assertIsNone(row['acceptance'])
        self.assertIn(dict(view_key='a_rg2b_g2_review',module='verify_p977_a_rg2b_g2',kind='g2',
                           dependency='a_rg2b_crossings'),roster['materializers'])
        support=registry.checked(p.ROOT)['accepted_generic_runtime_support']
        self.assertEqual(len(support),8)
        self.assertNotIn(gate.NOMINATED,support)
        self.assertEqual(registry.project_review(p.ROOT,row,checked,support),checked)
        self.assertEqual(checked['catalog_cells'],28)
        self.assertEqual(checked['numerical_tests_rerun'],0)
        self.assertEqual(checked['supplemental_interface_methods'],1)
        self.assertEqual(checked['new_G2_support'],[])
        self.assertFalse(checked['G2_accepted'])


if __name__=='__main__':unittest.main()
