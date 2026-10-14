"""Small native parity, writer-stage discrimination, and evidence pressure."""
from copy import deepcopy
from dataclasses import replace
import unittest
import p984g_apc_staged as p


def small():
    s=deepcopy(p.prior.read(p.prior.PREPARED)['source'])
    s['graph']['live_node_ids']=['a','b','c']
    s['graph']['edges']=[dict(edge_id=str(i),kind='boundary',tail=dict(node_id=u,port=1),head=dict(node_id=v,port=4))
        for i,(u,v) in enumerate((('a','b'),('b','c'),('c','a')))]
    for role in ('current','reset'):s['roles'][role].update(C=[2.25,2.,1.75],W_A=[1.00001,.99999,1.])
    return s


class APCStaged(unittest.TestCase):
    def test_small_native_complete_step_parity(self):
        from pygrc.models.grc_v4_pc import ProvisionalCandidatePCStep
        d=p.feasible.mechanical;old=p.prior.read(p.prior.PREPARED);s=small()
        graph=d.GRC9V4PortGraph.from_payload({k:v for k,v in s['graph'].items() if k!='graph_digest'})
        profile=d.profile_for(graph,'A_PC',old['selected_configuration'])
        s['profile']=profile.to_payload();s['graph']=graph.to_envelope()
        spec=d.native.GRC9V4Specialization(d.FrozenJSONMap(old['specialization']['resolved']),d.FrozenJSONMap(old['specialization']['identity_payload']))
        roles={r:d.authority(x,3) for r,x in s['roles'].items()}
        with p.ctx.workprec(p.BITS),d.exact_backend(d.ExactBackend.FLINT):
            seed=d.make_state(graph,profile,spec,roles,'A_PC')
            before=replace(seed.inputs,dt=2**-12,Q_target=6.)
            step=ProvisionalCandidatePCStep(before,d.GRC9V4CandidateADifferentialReference(graph))
            actual=p.analyze(s,'current',before.dt)
            for oracle,native in ((actual['initial'],step.read),(actual['final'],step.restart)):
                point=native.point
                for key,values in (('potential',point.potential.values),('baseline',point.baseline.values),
                    ('drive',point.W_hat_A),('current',point.current.values),('flux',point.read.flux.values),('flat',point.read.causal_flat.values)):
                    self.assertEqual(oracle[key],list(values),key)
                self.assertEqual(p.unpack(oracle['source']),[list(row) for row in native.structural_source.increment])
            self.assertEqual(actual['C'],list(step.next_inputs.current.C))
            self.assertEqual(actual['W_A'],list(step.next_inputs.current.W_A))
            self.assertEqual([x for row in p.unpack(actual['Z']) for x in row],list(step.next_inputs.current.Z_4))

    def test_wrong_stage_and_mechanism_controls(self):
        with p.ctx.workprec(p.BITS):
            s=small();md=p.model(s,'current');r=p.analyze(s,'current',2**-12)
            stale=p.writer_drive(md,list(map(float,md['c'])),r['initial']['current'])
            self.assertNotEqual(stale,r['writer_target'])
            z=[[float(p.prior.carrier(s,'current',3)[i]) if i==j else 0. for j in range(3)] for i in range(3)]
            wrong,_=p.write_z(z,p.unpack(r['final']['source']),2**-12,md['params']['realization']['tau_PC'])
            self.assertNotEqual(wrong,p.unpack(r['Z']))
            self.assertGreater(r['stale_Z_final_current_changed_coordinates'],0)
            off=deepcopy(s);off['profile']['params_resolved']['candidate']['chi_A']=0
            no=p.read(p.model(off,'current'),z)
            self.assertEqual(no['flux'],[0,0,0]);self.assertEqual(no['source']['entries'],[])

    def test_writer_rounding_boundaries_and_sparse_pressure(self):
        from pygrc.models.grc_v4_pc import scalar_zoh
        from pygrc.models.grc_v4_candidate_a import candidate_a_log_interpolation
        with p.ctx.workprec(p.BITS):
            for dt in (0.,2**-12,1.,2.):
                w=[.5,1.,1.0001];drive=[1.,.5,1.0001]
                self.assertEqual(p.write_w(w,drive,dt,1.)[0],list(candidate_a_log_interpolation(tuple(w),tuple(drive),dt,1.)))
                z=[[1.,-1.],[-1.,0.]];s=[[0.,1.],[1.,0.]]
                result=p.write_z(z,s,dt,1.)[0]
                self.assertEqual([x for row in result for x in row],list(scalar_zoh(tuple(x for row in z for x in row),tuple(x for row in s for x in row),dt,1.)))
            with self.assertRaises(ValueError):p.unique(p.a(1).union(p.a(1+2**-52)))
            with self.assertRaises(ValueError):p.hodge([[-2.,0.],[0.,0.]],1)
            with self.assertRaises(ValueError):p.unpack(dict(size=2,entries=[[0,1,1.],[0,1,1.]]))
            self.assertEqual(p.unpack(p.sparse([[0.,1.],[1.,0.]])),[[0.,1.],[1.,0.]])

    def test_retained_full_carrier_and_scope(self):
        v=p.check_retained()
        for c in v['cases']:
            r=c['result'];self.assertGreater(r['nonzero_offdiagonal_carrier_entries'],0)
            self.assertTrue(r['final_read_executed']);self.assertFalse(r['native_admission'])
        for mutate in (lambda v:v.update(native_steps=4),lambda v:v.update(ready_for_8_4h=True),
            lambda v:v['cases'][0]['result'].update(carrier_writer_stage='fresh_source'),
            lambda v:v['cases'][0]['result'].update(final_read_executed=False),
            lambda v:v['cases'][0]['result']['W_A'].__setitem__(0,.75)):
            bad=deepcopy(v);mutate(bad)
            with self.assertRaises(ValueError):p.check_retained(p.prior.seal(bad))


if __name__=='__main__':unittest.main()
