"""Focused PC writer, full-point freshness, charge and history pressure."""
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
import unittest
import p984h_apc_campaign as c
from test_p984g_apc_staged import small


def fixture():
    p=c.prep;s=small();d=p.d;old=c.p.prior.read(c.p.prior.PREPARED)
    graph=d.GRC9V4PortGraph.from_payload({k:v for k,v in s['graph'].items() if k!='graph_digest'})
    s['graph']=graph.to_envelope();s['profile']=d.profile_for(graph,'A_PC',old['selected_configuration']).to_payload()
    s['roles']['reset'].update(C=[2.125,2.,1.875],W_A=[.99999,1.00001,1.])
    before,_=p.prior.inputs_for(s,'current')
    return replace(before,Q_target=6.,dt=c.DT)


class CampaignTests(unittest.TestCase):
    def test_mixed_node_ids_preserve_non_event_labels(self):
        for value in (0,29,'0','oldish/node','ordinary'):
            self.assertEqual(c.event_label_image(value,'old','new'),value)
        self.assertEqual(c.event_label_image('old/satellite/2','old','new'),'new/satellite/2')

    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        self.stack.enter_context(c.prep.exact_backend(c.prep.ExactBackend.FLINT))
        self.stack.enter_context(c.prep.numerical_policy(c.prep.NumericalPolicy.CERTIFIED_ARB_256))
        self.stack.enter_context(c.prep.matrix_operation())

    def test_small_both_writers_full_point_and_independent_signs(self):
        before=fixture();e=c.observe(before,effects=True);after=c.check_step(e,before)
        self.assertEqual(after.reset,before.reset)
        self.assertNotEqual(after.current.Z_4,before.current.Z_4)
        self.assertNotEqual(after.current.W_A,before.current.W_A)
        self.assertGreater(c.q(e['carrier_separation']['margin']),0)
        self.assertTrue(all(c.q(r['lower'])>0 for r in e['oracle']['resource_bounds']))
        md=c.p.model(c.subject(before),'current')
        with c.p.ctx.workprec(c.p.BITS):
            wrong=c.p.writer_drive(md,list(before.current.C),e['reads']['current']['actual']['current'])
            wrongz,_=c.p.write_z(c.zrows(before.current),c.p.unpack(e['reads']['final']['oracle']['source']),before.dt,md['params']['realization']['tau_PC'])
        self.assertNotEqual(wrong,e['oracle']['drive'])
        self.assertNotEqual(c.p.sparse(wrongz),e['oracle']['Z'])

    def test_resealed_stale_geometry_authority_and_history_rejected(self):
        before=fixture();e=c.observe(before)
        mutations=[lambda x:x['next_inputs']['reset']['C'].__setitem__(0,0.),
            lambda x:x['reads']['final']['actual'].update(H=deepcopy(x['reads']['current']['actual']['H'])),
            lambda x:x['next_inputs'].update(time=1.),
            lambda x:x['oracle'].update(Z_stage='fresh_final_read'),
            lambda x:x['reads']['reset']['actual']['W_A'].__setitem__(0,.5),
            lambda x:x['oracle']['resource_bounds'][0].update(lower='-1'),
            lambda x:x.update(native_events=1)]
        for mutate in mutations:
            bad=deepcopy(e);mutate(bad)
            with self.assertRaises((ValueError,AssertionError)):c.check_step(bad,before)

    def test_charge_uses_declared_inequality_not_extra_exact_zero(self):
        before=fixture();e=c.observe(before);after=c.check_step(e,before)
        altered=replace(after,current=replace(after.current,C=(after.current.C[0]+2**-45,*after.current.C[1:])))
        qnew=c.prep.prior.charge_helpers.pairwise(altered.current.C)
        receipt=dict(target_charge=before.Q_target,admitted_charge=qnew,residual=float(c.q(qnew)-c.q(before.Q_target)))
        c.charge_check(before,altered,receipt)
        with self.assertRaises(ValueError):c.charge_check(before,altered,dict(receipt,residual=1.))

    def test_noncanonical_carrier_cannot_hide_extra_or_duplicate_coordinates(self):
        for z in (dict(size=2,entries=[[0,1,1.],[0,1,1.]]),dict(size=2,entries=[[2,0,1.]])):
            with self.assertRaises(ValueError):c.p.unpack(z)
        self.assertTrue(c.contains({'carrier_archives':[{'old':1}]},{'old':1}))
        self.assertFalse(c.contains({'carrier_archives':[]},{'old':1}))


if __name__=='__main__':unittest.main()
