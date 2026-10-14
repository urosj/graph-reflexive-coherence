"""Targeted full-point freshness, mechanism and retained-scope pressure."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import p984g_apc_hardening as h
from test_p984g_apc_staged import small
p=h.p


class APCHardening(unittest.TestCase):
    def test_history_companion_small_native_complete_chain_parity(self):
        from test_p984g_apc_staged import APCStaged
        s=small()
        for role in ('current','reset'):
            s['roles'][role]['W_A']=[p.rn(p.q(x)*p.q('7/8')) for x in s['roles'][role]['W_A']]
        with patch('test_p984g_apc_staged.small',return_value=s):
            APCStaged().test_small_native_complete_step_parity()

    def test_selection_and_lineage_not_target_fit(self):
        self.assertEqual(h.selection()['unconstrained_scale'],'11/16')
        self.assertEqual(h.selection()['scale'],'7/8')
        self.assertGreater(h.q(h.selection()['minimum_leading_rate']),0)
        v=p.feasible.check_retained();s=h.companion(v)
        for role in ('current','reset'):
            old=dict(zip((e['edge_id'] for e in s['source']['graph']['edges']),s['source']['roles'][role]['W_A']))
            for e,w in zip(s['target']['graph']['edges'],s['target']['roles'][role]['W_A']):
                self.assertEqual(w,old.get(e['edge_id'],1.))
            self.assertEqual(s['target']['roles'][role]['Z_4'],{'recipe':'zero_v1'})
            self.assertEqual(s['source']['roles'][role]['C'],v['source']['roles'][role]['C'])
        self.assertNotIn('scientific_digest',s['source'])

    def test_original_target_current_blindness_does_not_bypass_geometry(self):
        rows=h.original_pressure(p.check_retained(),p.feasible.read())
        for row in rows:
            self.assertTrue(row['stale_H_resealed_rejected'])
            if row['graph']=='target':self.assertEqual(row['stale_Z_current_changed_coordinates'],0)

    def test_full_final_read_rejects_resealed_wrong_operands_and_fields(self):
        with p.ctx.workprec(p.BITS):
            s=small();r=p.analyze(s,'current',2**-12);h.compare_final(s,'current',r)
            mutations=[lambda b:b['C'].__setitem__(0,b['C'][0]+.001),
                lambda b:b['W_A'].__setitem__(0,.75),
                lambda b:b.update(Z=p.sparse([[0.]*3 for _ in range(3)])),
                lambda b:b['final']['current'].__setitem__(0,0.),
                lambda b:b['final']['flat'].__setitem__(0,0.),
                lambda b:b['final'].update(source=p.sparse([[0.]*3 for _ in range(3)]))]
            for mutate in mutations:
                bad=deepcopy(r);mutate(bad)
                bad['final']['point_digest']=h.point_digest(s,'current',bad)
                with self.assertRaises(ValueError):h.compare_final(s,'current',bad)

    def test_retained_separation_and_scope(self):
        v=h.check_retained()
        for mutate in (lambda b:b.update(native_steps=4),lambda b:b.update(ready_for_8_4h=True),
            lambda b:b['cases'][2]['carrier_separation'].update(margin='0'),
            lambda b:b['subjects']['target']['roles']['current']['W_A'].__setitem__(0,.75)):
            bad=deepcopy(v);mutate(bad)
            with self.assertRaises(ValueError):h.check_retained(p.prior.seal(bad))


if __name__=='__main__':unittest.main()
