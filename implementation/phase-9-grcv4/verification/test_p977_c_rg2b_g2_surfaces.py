"""Actual G2 materializer, trusted projection and unchanged discovery scope."""

import unittest
import phase9_implementation_policy as p
import profile_g2_registry as registry
import verify_p977_c_rg2b_g2 as gate


class SurfaceTests(unittest.TestCase):
    def test_current_g2_checker_projects_only_the_pinned_acceptance(self):
        roster=registry.registry(p.ROOT)
        bounded=roster['reconciliation_views']['c_rg2b_crossings']
        self.assertTrue(bounded['user_accepted'])
        checked=registry._checker(p.ROOT,'verify_p977_c_rg2b_g2')(bounded_acceptance=bounded)
        row=next(r for r in roster['records'] if r['complete_profile_id']==gate.NOMINATED)
        self.assertEqual(row['adapter'],'exact_profile_v1')
        self.assertEqual(row['state'],'accepted')
        self.assertIsNotNone(row['acceptance'])
        self.assertIn(dict(view_key='c_rg2b_g2_review',module='verify_p977_c_rg2b_g2',kind='g2',
                           dependency='c_rg2b_crossings'),roster['materializers'])
        support=registry.checked(p.ROOT)['accepted_generic_runtime_support']
        self.assertEqual(len(support),10)
        self.assertIn(gate.NOMINATED,support)
        projected=registry.project_review(p.ROOT,row,checked,support)
        self.assertTrue(projected['G2_accepted'])
        self.assertEqual(projected['new_G2_support'],[gate.NOMINATED])
        self.assertEqual(checked['catalog_cells'],33)
        self.assertEqual(checked['numerical_tests_rerun'],0)
        self.assertEqual(checked['supplemental_interface_methods'],1)
        self.assertEqual(checked['new_G2_support'],[])
        self.assertFalse(checked['G2_accepted'])


if __name__=='__main__':unittest.main()
