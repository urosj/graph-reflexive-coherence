"""Focused pressure: joint-root bounds, fixed rows, both roles and fail-closed scope."""
from copy import deepcopy
import unittest
import numpy as np
import p984g_aci_investigation as p


class ACIInvestigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.declaration=p.read(p.PREPARED)

    def cert(self,s,role='current'):
        with p.ctx.workprec(p.BITS):
            return p.certificate(s,role,self.declaration['selected_configuration']['ordinary_dt'])

    def test_four_joint_roots_do_not_imply_both_role_continuation(self):
        value=p.check()
        self.assertEqual(len(value['cases']),4)
        for c in value['cases']:
            self.assertTrue(c['exact_real_unique_joint_root'])
            self.assertLess(p.q(c['bounds']['contraction_upper']),1)
            self.assertFalse(c['native_stopping_or_positivity_claim'])
        self.assertEqual([c['exact_real_first_step_resources_nonnegative'] for c in value['cases']],[True,True,True,False])
        negative=value['cases'][3]['certified_negative_vertices']
        self.assertEqual(len(negative),1)
        self.assertTrue(negative[0]['vertex'].endswith('/extra/1/1'))
        self.assertLess(p.q(negative[0]['upper']),0)

    def test_history_role_is_not_interchangeable(self):
        s=deepcopy(self.declaration['target'])
        s['roles']['reset']['W_A']=s['roles']['current']['W_A']
        self.assertTrue(self.cert(s,'reset')['exact_real_first_step_resources_nonnegative'])
        # Diagnostic ablation only: never replace the declared reset history.
        self.assertFalse(self.cert(self.declaration['target'],'reset')['exact_real_first_step_resources_nonnegative'])

    def test_fixed_rows_against_public_backend_identity_and_exact_operands(self):
        from pygrc.models.grc_9_v4_topology import GRC9V4CandidateADifferentialReference, GRC9V4PortGraph
        from pygrc.models.grc_v4_geometry import VertexScalar
        for graph in ('source','target'):
            s=self.declaration[graph]
            payload={k:v for k,v in s['graph'].items() if k!='graph_digest'}
            backend=GRC9V4CandidateADifferentialReference(GRC9V4PortGraph.from_payload(payload))
            self.assertEqual(backend.identity,s['profile']['params_resolved']['candidate']['descriptor_backend_id'])
            for role in ('current','reset'):
                _,_,_,_,rows=p.operands(s,role)
                state=s['roles'][role]
                actual=backend.rebuild_exact(VertexScalar(backend.graph,tuple(state['C'])),tuple(state['W_A']))
                self.assertEqual(rows,[[p.q(str(x)) for x in row] for row in actual])

    def test_domain_equalities_and_outside_cases(self):
        args=dict(radius=p.q('1/8'),displacement=p.q('1/8'),contraction=p.q('1/2'),margin=1,condition=2,limit=2)
        p.domain(**args)
        for change in (dict(radius=1),dict(radius=0),dict(displacement=p.q('1/8')+p.q('1/1099511627776')),
                       dict(contraction=1),dict(margin=0),dict(condition=3)):
            with self.subTest(change=change),self.assertRaises(ValueError):p.domain(**{**args,**change})

    def test_hypothesis_mutations(self):
        changes=[lambda s:s['roles']['current']['W_A'].__setitem__(0,0),
            lambda s:s['roles']['current']['C'].__setitem__(0,float('nan')),
            lambda s:s['roles']['current'].update(Z_4=[0]),
            lambda s:s['profile']['params_resolved']['candidate'].update(W_floor=2),
            lambda s:s['profile']['params_resolved']['candidate'].update(chi_A=2**30),
            lambda s:s['profile']['params_resolved']['geometry'].update(kappa_H=2**60),
            lambda s:s['graph']['edges'][0]['tail'].update(port=0),
            lambda s:s['roles']['current']['W_A'].pop(),
            lambda s:s['profile']['params_resolved']['geometry'].update(star_cover_id='unknown')]
        for change in changes:
            s=deepcopy(self.declaration['source']);change(s)
            with self.subTest(change=change),self.assertRaises(ValueError):self.cert(s)

    def test_small_cyclic_dense_lipschitz_and_joint_geometry(self):
        s=deepcopy(self.declaration['source'])
        s['graph']['live_node_ids']=['a','b','c']
        s['graph']['edges']=[dict(edge_id=str(i),tail=dict(node_id=u,port=1),head=dict(node_id=v,port=4))
            for i,(u,v) in enumerate((('a','b'),('b','c'),('c','a')))]
        s['roles']['current'].update(C=[2.25,2,1.75],W_A=[1.00001,.99999,1])
        cert=self.cert(s)['bounds'];b,ends,c,w,rows=p.operands(s,'current')
        c,w,rows=np.array(c,dtype=float),np.array(w,dtype=float),np.array(rows,dtype=float)
        cp=s['profile']['params_resolved']['candidate'];kh=s['profile']['params_resolved']['geometry']['kappa_H']
        def read(h):
            baseline=-cp['eta']*w*(b.T@b@(cp['kappa_c']*np.diag(w)+cp['kappa_Ah']*(h-np.eye(3)))@b.T@c)
            drive=np.array([np.exp(-(cp['alpha']*(c[u]+c[v])+cp['beta']*np.sum((rows[u]-rows[v])**2)+cp['gamma']*baseline[i]**2)/2) for i,(u,v) in enumerate(ends)])
            contrast=(w-drive)/(w+drive)
            current=np.linalg.solve(np.diag(1-cp['zeta_A']*cp['chi_A']*contrast),baseline)
            flat=np.linalg.solve(h,cp['chi_A']*contrast*current)
            generated=np.eye(3)+kh*cp['zeta_A']*(.5*np.ones((3,3))+.5*np.eye(3))*np.outer(flat,flat)
            return current,flat,generated
        h0=np.eye(3);j0,f0,t0=read(h0)
        for direction in (np.diag([1,-1,0]),np.array([[0,1,0],[1,0,0],[0,0,1]])):
            h=h0+direction*float(p.q(cert['radius']))/4
            j,f,t=read(h);distance=np.linalg.norm(h-h0,'fro')
            self.assertLess(np.linalg.norm(j-j0),float(p.q(cert['current_lipschitz_upper']))*distance)
            self.assertLess(np.linalg.norm(f-f0),float(p.q(cert['flat_lipschitz_upper']))*distance)
            # Binary64 diagonal addition may erase the tiny source. Test its
            # full unrounded outer-product norm, not a claimed visible H-I.
            source=kh*cp['zeta_A']*(.5*np.ones((3,3))+.5*np.eye(3))*np.outer(f,f)
            self.assertLess(np.linalg.norm(source,'fro'),float(p.q(cert['displacement_upper'])))

    def test_scope_and_endpoint_forgery(self):
        value=p.read(p.RESULTS)
        for field in ('native_roots','native_steps','ready_for_8_4h','user_accepted'):
            x=deepcopy(value);x[field]=1
            with self.subTest(field=field),self.assertRaises(ValueError):p.check(p.seal(x))
        x=deepcopy(value);x['cases'][3]['certified_negative_vertices']=[]
        with self.assertRaises(ValueError):p.check(p.seal(x))


if __name__=='__main__':unittest.main()
