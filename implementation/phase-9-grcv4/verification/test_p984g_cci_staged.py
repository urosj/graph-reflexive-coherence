"""Pressure the joint error bridge and rounded-versus-analytic distinction."""
from copy import deepcopy
import unittest
import json
from flint import arb,arb_mat
import p984g_cci_staged as p


def small_subject():
    s=deepcopy(p.read(p.prior.PREPARED)['source'])
    s['graph']['live_node_ids']=['a','b','c']
    s['graph']['edges']=[dict(edge_id=str(i),tail=dict(node_id=u),head=dict(node_id=v))
        for i,(u,v) in enumerate((('a','b'),('b','c'),('c','a')))]
    s['profile']['params_resolved']['candidate']['W_C_tr']={str(i):1 for i in range(3)}
    s['roles']['current']['C']=[2.25,2,1.75]
    return s


class StagedMath(unittest.TestCase):
    def test_current_defect_cannot_be_dropped(self):
        s=small_subject();bounds=p.prior.certificate(s,'current')['bounds']
        with p.ctx.workprec(p.iv.BITS):
            exact=p.bridge(bounds,16,p.q('1/8589934592'),p.q('1/9007199254740992'),0,0)
            perturbed=p.bridge(bounds,16,p.q('1/8589934592'),p.q('1/9007199254740992'),'1/1000',0)
        self.assertEqual(p.q(exact['joint_error_upper']),0)
        for name in ('current_defect_upper','source_defect_upper','geometry_error_upper','current_error_upper'):
            self.assertGreater(p.q(perturbed[name]),0)
        self.assertGreater(p.q(perturbed['current_error_upper']),p.q('1/1000'))
        altered={**bounds,'contraction_upper':'1'}
        with self.assertRaises(ValueError):p.bridge(altered,16,0,1,0,0)

    def test_rounding_uncertainty_cannot_be_called_a_current(self):
        with self.assertRaises(ValueError):p.unique(arb_mat([[arb(1).union(arb(1+2**-52))]]))

    def test_small_full_matrix_resolvent_and_joint_bridge(self):
        s=small_subject();bv,params=p.prior.shared.graph_data(s);cp=params['candidate']
        with p.ctx.workprec(p.iv.BITS):
            b=p.iv.matrix(bv);h=p.iv.matrix([[1.01,.001,0],[.001,.99,.002],[0,.002,1.02]])
            j=p.iv.matrix([[.25],[-.5],[.75]]);t=arb('1.1')
            reduced=p.response(b,h,j,cp,t)
            literal=(p.iv.eye(3)+p.iv.a(cp['tau_C'])*t*h*b.transpose()*b).solve(j)
            for i in range(3):self.assertTrue(reduced[i,0].overlaps(literal[i,0]))
            result=p.analyze(s,'current',2**-12)
        self.assertTrue(result['independent_analytic_residual_pass'])
        json.dumps(result,allow_nan=False)
        self.assertGreater(p.q(result['analytic_current_residual_upper']),0)
        self.assertGreater(p.q(result['analytic_geometry_residual_upper']),0)
        self.assertGreater(p.q(result['exact_feedback_current_max_lower']),0)
        self.assertFalse(result['native_stopping_outcome_verified'])
        self.assertLess(p.q(result['reference_to_root_current_error_upper']),p.q(result['joint_root_bridge']['current_error_upper']))


class RetainedPressure(unittest.TestCase):
    def test_retained_scientific_and_scope_mutations(self):
        value=p.read(p.case_path('source','current'));p.check_case(value)
        for field in ('native_roots','native_steps','native_events','ready_for_8_4h','user_accepted'):
            v=deepcopy(value);v[field]=1
            with self.subTest(field=field),self.assertRaises(ValueError):p.check_case(p.seal(v))
        for edit in (lambda r:r['joint_root_bridge'].update(current_defect_upper='0'),
                     lambda r:r.update(generated_geometry_residual_squared='0'),
                     lambda r:r.update(native_stopping_outcome_verified=True),
                     lambda r:r['reference_current'].__setitem__(0,float('nan')),
                     lambda r:r['reference_continuity_proposal'].__setitem__(0,-1)):
            v=deepcopy(value);edit(v['result'])
            with self.assertRaises(ValueError):p.check_case(p.seal(v))


if __name__=='__main__':unittest.main()
