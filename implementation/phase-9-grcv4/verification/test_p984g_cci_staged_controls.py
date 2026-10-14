"""Small independent mechanism controls; never rerun the large research cases."""
from copy import deepcopy
import math
import unittest
import p984g_cci_staged as p
from test_p984g_cci_staged import small_subject


class MechanismControls(unittest.TestCase):
    def test_zero_geometry_gain_and_zero_readback_do_not_invent_feedback(self):
        for parameter in ('kappa_H','chi_C'):
            s=small_subject();params=s['profile']['params_resolved']
            params['geometry' if parameter=='kappa_H' else 'candidate'][parameter]=0
            with self.subTest(parameter=parameter),p.ctx.workprec(p.iv.BITS):
                r=p.analyze(s,'current',2**-12)
                self.assertEqual(r['generated_geometry_residual_squared'],'0')
                self.assertEqual(r['generated_nonzero_offdiagonals'],0)
                self.assertEqual(r['counterfactual_changed_current_coordinates'],0)
                self.assertEqual(r['reference_current'],r['counterfactual_current'])
                self.assertLessEqual(p.q(r['exact_feedback_current_max_lower']),0)
                self.assertEqual(p.q(r['joint_root_bridge']['geometry_error_upper']),0)

    def test_residual_threshold_cannot_add_a_hidden_iteration(self):
        s=small_subject()
        with p.ctx.workprec(p.iv.BITS):
            original=p.analyze(s,'current',2**-12)
            residual=float(p.q(original['analytic_joint_residual_upper']))
            for factor,passes in ((.5,False),(2,True)):
                changed=deepcopy(s)
                changed['profile']['params_resolved']['realization']['tolerance']=residual*factor
                actual=p.analyze(changed,'current',2**-12)
                self.assertEqual(actual['independent_analytic_residual_pass'],passes)
                self.assertEqual(actual['reference_current'],original['reference_current'])
                self.assertEqual(actual['counterfactual_current'],original['counterfactual_current'])
                self.assertFalse(actual['native_stopping_outcome_verified'])


if __name__=='__main__':unittest.main()
