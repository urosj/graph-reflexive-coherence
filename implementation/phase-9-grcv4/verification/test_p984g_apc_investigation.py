"""A_PC chart, diagonal-current, stage and scope pressure (no native campaign)."""
from copy import deepcopy
import unittest
import numpy as np
import p984g_apc_investigation as p


class APCInvestigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.v=p.read(p.PREPARED)

    def small(self):
        s=deepcopy(self.v['source']);s['graph']['live_node_ids']=['a','b','c']
        s['graph']['edges']=[dict(edge_id=str(i),tail=dict(node_id=u,port=1),head=dict(node_id=v,port=4))
            for i,(u,v) in enumerate((('a','b'),('b','c'),('c','a')))]
        s['roles']['current'].update(C=[2.25,2.,1.75],W_A=[1.00001,.99999,1.])
        return s

    def test_small_dense_current_and_old_carrier(self):
        s=self.small()
        with p.ctx.workprec(p.BITS):
            v=p.point(s,'current');cp=s['profile']['params_resolved']['candidate']
            b=v['b'];w=np.array(v['w'],dtype=float);c=np.array(v['c'],dtype=float);h=np.diag(np.array(v['h'],dtype=float))
            baseline=-cp['eta']*w*(b.T@b@(cp['kappa_c']*np.diag(w)+cp['kappa_Ah']*(h-np.eye(3)))@b.T@c)
            _,_,_,_,desc=p.operands(s,'current');desc=np.array(desc,dtype=float)
            drive=np.array([max(cp['W_floor'],np.exp(-(cp['alpha']*(c[u]+c[z])+cp['beta']*sum((desc[u]-desc[z])**2)+cp['gamma']*baseline[i]**2)/2)) for i,(u,z) in enumerate(v['ends'])])
            contrast=(w-drive)/(w+drive)
            current=np.linalg.solve(np.diag(1-cp['zeta_A']*cp['chi_A']*contrast),baseline)
            np.testing.assert_allclose(current,[float(x) for x in v['J']],rtol=1e-13,atol=1e-14)
            np.testing.assert_allclose(np.linalg.solve(h,cp['chi_A']*contrast*current),[float(x) for x in v['flat']],rtol=1e-9,atol=1e-14)
            off=p.point(s,'current',zero_readback=True)
            self.assertTrue(all(p.lo(x)<=y<=p.hi(x) for x,y in zip(off['J'],off['baseline'])))

    def test_chart_equalities_and_outside(self):
        bounds=(p.q(2),p.q('1/2'),p.q(1),p.q(3),p.q(1))
        p.admit_state([p.q(2)],[p.q('1/2')],[p.q(3)],bounds)
        for c,w,z in ((['-1'],['1'],['0']),(['2.0001'],['1'],['0']),(['1'],['1.0001'],['0']),(['1'],['1'],['3.0001'])):
            with self.assertRaises(ValueError):p.admit_state(list(map(p.q,c)),list(map(p.q,w)),list(map(p.q,z)),bounds)
        for mutation in (lambda s:s['profile']['params_resolved']['geometry'].update(kappa_H=1),
            lambda s:s['profile']['params_resolved']['candidate'].update(chi_A=2),
            lambda s:s['roles']['current'].update(Z_4={'recipe':'unknown'}),
            lambda s:s['roles']['current']['W_A'].__setitem__(0,0),
            lambda s:s['graph']['edges'][0]['tail'].update(port=0)):
            s=self.small();mutation(s)
            with p.ctx.workprec(p.BITS),self.assertRaises(ValueError):p.case(s,'current',2**-12)

    def test_floor_and_writer_timing(self):
        s=self.small();cp=s['profile']['params_resolved']['candidate'];cp.update(alpha=100.,beta=0.,gamma=0.)
        with p.ctx.workprec(p.BITS):
            v=p.point(s,'current')
            self.assertTrue(all(p.lo(x)==p.hi(x)==p.q(cp['W_floor']) for x in v['drive']))
            s=self.small();result=p.case(s,'current',2**-12)
            self.assertEqual(result['history_writer']['timing'],'postcontinuity_C_incoming_W_selected_current')
            self.assertTrue(result['carrier_next_in_ball'])
            cp=s['profile']['params_resolved']['candidate'];v=p.point(s,'current')
            after=[p.a(ci)-p.a(2**-12)*sum((int(x)*j for x,j in zip(row,v['J'])),p.arb(0)) for ci,row in zip(v['c'],v['b'])]
            desc=p.scalar.descriptors(s,after,list(map(p.a,v['w'])))
            true=p.floored_drive(cp,v['ends'],after,desc,v['J'])
            stale=v['drive']
            self.assertTrue(any(p.lo(abs(x-y))>0 for x,y in zip(true,stale)))

    def test_retained_scope_and_bounds(self):
        value=p.check()
        self.assertEqual([(c['graph'],c['role']) for c in value['cases']],list(p.rows.shared.CASES))
        self.assertTrue(all(p.q(c['whole_chart']['source_slack'])>0 for c in value['cases']))
        self.assertEqual([c['resource_sign'] for c in value['cases']],['nonnegative']*3+['excluded'])
        excluded=value['cases'][-1]
        self.assertEqual(len(excluded['negative_vertices']),1)
        self.assertTrue(excluded['negative_vertices'][0]['vertex'].endswith('/extra/1/1'))
        self.assertIsNone(excluded['history_writer'])
        self.assertEqual(len(excluded['leading_empty_node_constraints']),5)
        self.assertLess(p.q(next(r for r in excluded['leading_empty_node_constraints'] if r['node']=='extra/1/1')['original_rate_upper']),0)
        for key in ('native_steps','native_events','ready_for_8_4h','user_accepted'):
            changed=deepcopy(value);changed[key]=1
            with self.assertRaises(ValueError):p.check(p.seal(changed))


if __name__=='__main__':unittest.main()
