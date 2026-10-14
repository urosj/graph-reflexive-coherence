"""Scientific pressure for the large-CI exact-real investigation, not native runs."""
from copy import deepcopy
import unittest
import numpy as np
from flint import fmpq
import p984g_cci_investigation as p


class CIInvestigation(unittest.TestCase):
    def test_strict_domain_boundaries(self):
        args=dict(n=4,radius=p.q('1/16'),cutoff=p.q('1/64'),beta=p.q('1/8'),
                  displacement=p.q('1/16'),contraction=p.q('1/2'),condition=p.q(2),limit=p.q(3))
        self.assertGreater(p.conditions(**args),0)
        for change in (dict(radius=1),dict(radius=-1),dict(cutoff=0),
                       dict(cutoff=p.q('15/192')),dict(beta=1),dict(beta=-1),
                       dict(displacement=p.q('1/8')),dict(contraction=1),dict(condition=4)):
            with self.subTest(change=change),self.assertRaises(ValueError):p.conditions(**{**args,**change})

    def test_declared_cases_and_reference_residual_caveat(self):
        value=p.calculate()
        self.assertEqual(len(value['cases']),4)
        for c in value['cases']:
            self.assertTrue(c['exact_real_unique_root'])
            self.assertTrue(c['reference_pair_already_within_exact_real_residual_tolerance'])
            self.assertLess(p.q(c['bounds']['contraction_upper']),1)
            self.assertFalse(c['native_first_iteration_prediction_verified'])
        self.assertFalse(value['ready_for_8_4h'])

    def test_graph_parameter_and_history_hypotheses(self):
        base=p.read(p.PREPARED)['source']
        changes=[lambda s:s['graph']['edges'].pop(),
                 lambda s:s['profile']['params_resolved']['candidate'].update(tau_C=-1),
                 lambda s:s['profile']['params_resolved']['candidate'].update(chi_C=2**40),
                 lambda s:s['profile']['params_resolved']['candidate'].update(kappa_Phi_C=float('nan')),
                 lambda s:s['profile']['params_resolved']['geometry'].update(star_cover_id='unknown'),
                 lambda s:s['roles']['current'].update(Z_4=[0]),
                 lambda s:s['roles']['current']['C'].__setitem__(0,-1)]
        for change in changes:
            s=deepcopy(base);change(s)
            with self.subTest(change=change),self.assertRaises(ValueError):p.certificate(s,'current')
        s=deepcopy(base)
        s['graph']['edges'][0]['head']=deepcopy(s['graph']['edges'][0]['tail'])
        with self.assertRaises(ValueError):p.certificate(s,'current')

    def test_small_dense_reduction_and_frobenius_lipschitz(self):
        # A triangle is deliberately cyclic; old tree hypotheses cannot justify it.
        s=deepcopy(p.read(p.PREPARED)['source']);g=s['graph']
        g['live_node_ids']=['a','b','c'];g['edges']=[dict(edge_id=str(i),tail=dict(node_id=u),head=dict(node_id=v))
            for i,(u,v) in enumerate((('a','b'),('b','c'),('c','a')))]
        params=s['profile']['params_resolved'];cp=params['candidate']
        cp['W_C_tr']={str(i):1 for i in range(3)}
        params['realization']['contraction_domain_id']='ci_reference_frobenius_ball_v1:0x1.0000000000000p-4'
        s['roles']['current']['C']=[2.25,2,1.75]
        cert=p.certificate(s,'current')['bounds'];b,_=p.shared.graph_data(s)
        c=np.array(s['roles']['current']['C']);t=np.exp(cp['kappa_M_C']*np.tanh(c.mean()/cp['C_ref']))
        mats=[np.eye(3),np.eye(3)+np.diag([.01,-.02,.015]),
              np.eye(3)+np.array([[.01,.005,0],[.005,-.01,.003],[0,.003,.02]])]
        values=[]
        for h in mats:
            literal=p.shared.dense_point(b,c,h,cp)
            j0=-cp['eta_C']*cp['kappa_Phi_C']*t*b.T@b@h@b.T@c
            beta=cp['zeta_C']*cp['chi_C']
            v=np.linalg.solve((1-beta)*np.eye(3)+cp['tau_C']*t*h@b.T@b,j0)
            j=j0+beta*v;f=cp['chi_C']*np.linalg.solve(h,v)
            np.testing.assert_allclose(j,literal['current'],atol=1e-12,rtol=1e-12)
            np.testing.assert_allclose(f,literal['causal_flat'],atol=1e-12,rtol=1e-12)
            self.assertLess(np.linalg.norm(f),float(p.q(cert['flat_upper'])))
            values.append((j,f))
        for i in range(1,len(mats)):
            distance=np.linalg.norm(mats[i]-mats[0],'fro')
            self.assertLess(np.linalg.norm(values[i][1]-values[0][1]),float(p.q(cert['flat_lipschitz_upper']))*distance)
            self.assertLess(np.linalg.norm(values[i][0]-values[0][0]),float(p.q(cert['current_lipschitz_upper']))*distance)

    def test_retained_scope_and_bound_mutations(self):
        value=p.check()
        for key in ('native_roots','native_steps','native_events','ready_for_8_4h','user_accepted'):
            x=deepcopy(value);x[key]=1
            with self.subTest(key=key),self.assertRaises(ValueError):p.check(p.seal(x))
        x=deepcopy(value);x['cases'][2]['bounds']['contraction_upper']='0'
        with self.assertRaises(ValueError):p.check(p.seal(x))


if __name__=='__main__':unittest.main()
