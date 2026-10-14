"""Staging, full-joint evidence and wrong-mechanism pressure on the A oracle."""
from copy import deepcopy
import math
import unittest
import p984g_aci_staged as p


def small():
    s=deepcopy(p.feasible.prior.read(p.feasible.prior.PREPARED)['source'])
    s['graph']['live_node_ids']=['a','b','c']
    s['graph']['edges']=[dict(edge_id=str(i),kind='boundary',tail=dict(node_id=u,port=1),head=dict(node_id=v,port=4))
        for i,(u,v) in enumerate((('a','b'),('b','c'),('c','a')))]
    for role in ('current','reset'):s['roles'][role].update(C=[2.25,2,1.75],W_A=[1.00001,.99999,1])
    return s


class ACIStaged(unittest.TestCase):
    def test_rounding_ties_and_explicit_inconclusive_failure(self):
        with p.ctx.workprec(p.BITS):
            self.assertEqual(p.rn(1+p.q('1/9007199254740992')),1.0)
            self.assertEqual(p.rn(1+p.q('3/9007199254740992')),1+2**-51)
            self.assertEqual(p.unique(p.a(0)),0)
            with self.assertRaises(ValueError):p.unique(p.a(1).union(p.a(math.nextafter(1,2))))

    def test_small_primitive_parity_without_a_native_root(self):
        from pygrc.models.grc_v4_candidate_a import CandidateACurrent
        from pygrc.models.grc_v4_geometry import OneFormHodge,GRCV4Geometry
        from dataclasses import replace
        d=p.feasible.prepared;old=p.feasible.prior.read(p.feasible.prior.PREPARED);s=small()
        payload={k:v for k,v in s['graph'].items() if k!='graph_digest'}
        graph=d.GRC9V4PortGraph.from_payload(payload)
        profile=d.profile_for(graph,'A_CI',old['selected_configuration'])
        s['profile']=profile.to_payload();s['graph']=graph.to_envelope()
        spec=d.native.GRC9V4Specialization(d.FrozenJSONMap(old['specialization']['resolved']),d.FrozenJSONMap(old['specialization']['identity_payload']))
        roles={r:d.authority(x,3) for r,x in s['roles'].items()}
        state=d.make_state(graph,profile,spec,roles,'A_CI');backend=d.GRC9V4CandidateADifferentialReference(graph)
        md=p.model(s,'current');h=p.eye(3)
        with p.ctx.workprec(p.BITS),d.exact_backend(d.ExactBackend.FLINT):
            for _ in range(2):
                rows=tuple(tuple(p.unique(h[i,j]) for j in range(3)) for i in range(3))
                ref=state.inputs.geometry.reference
                inputs=replace(state.inputs,geometry=GRCV4Geometry(ref,OneFormHodge(ref.graph,rows)))
                native=CandidateACurrent(inputs,backend);actual=p.represented(md,h)
                for key,values in (('potential',native.potential.values),('baseline',native.baseline.values),
                                   ('drive',native.W_hat_A),('current',native.current.values),
                                   ('flux',native.read.flux.values),('flat',native.read.causal_flat.values)):
                    self.assertEqual(actual[key],list(values),key)
                h=p.image(md,actual['flat'],staged=True)

    def test_zero_feedback_and_wrong_stage_controls(self):
        with p.ctx.workprec(p.BITS):
            s=small();md=p.model(s,'current');r=p.represented(md,p.eye(3));h=p.image(md,r['flat'],staged=True)
            self.assertGreater(p.norm(h-p.eye(3)),0)
            s['profile']['params_resolved']['candidate']['chi_A']=0
            disabled=p.model(s,'current');off=p.represented(disabled,p.eye(3))
            self.assertEqual(off['flux'],[0,0,0]);self.assertEqual(off['flat'],[0,0,0])
            self.assertEqual(p.norm(p.image(disabled,off['flat'],staged=True)-p.eye(3)),0)
            s=small();s['roles']['current']['W_A']=[.75,1.2,1.1]
            md=p.model(s,'current');r=p.represented(md,p.eye(3))
            self.assertNotEqual(r['baseline'],r['current'])
            bounds=p.prior.certificate(s,'current',1)['bounds']
            wrong=deepcopy(r);wrong['current']=r['baseline']
            self.assertFalse(p.stage(md,p.eye(3),wrong,bounds)['analytic_residual_pass'])

    def test_bridge_needs_current_defect_not_geometry_alone(self):
        with p.ctx.workprec(p.BITS):
            s=small();md=p.model(s,'current');bounds=p.prior.certificate(s,'current',1)['bounds']
            r=p.bridge(bounds,md['p'],md['params']['geometry']['kappa_H'],p.q('1/1000000'),0)
            self.assertGreater(p.q(r['current_error_upper']),0)
            self.assertGreater(p.q(r['geometry_error_upper']),0)
            with self.assertRaises(ValueError):p.bridge({**bounds,'contraction_upper':'1'},md['p'],1,0,0)

    def test_retained_full_joint_scope_and_mutations(self):
        value=p.check_retained()
        self.assertEqual(len(value['cases']),4)
        for c in value['cases']:
            r=c['result'];self.assertTrue(r['two_consecutive_independent_residual_passes'])
            self.assertFalse(r['native_stopping_outcome_verified'])
            self.assertGreater(p.q(r['exact_feedback_current_max_lower']),0)
        for mutate in (lambda x:x.update(native_roots=4),lambda x:x.update(ready_for_8_4h=True),
                       lambda x:x['cases'][0]['result'].update(selected_joint_point_digest='wrong'),
                       lambda x:x['cases'][0]['result']['stages'][0]['joint_root_bridge'].update(current_error_upper='0')):
            changed=deepcopy(value);mutate(changed)
            with self.assertRaises(ValueError):p.check_retained(p.prior.seal(changed))


if __name__=='__main__':unittest.main()
