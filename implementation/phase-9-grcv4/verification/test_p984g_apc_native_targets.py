"""Numeric-type binding regression and full corrected target evidence."""
from copy import deepcopy
import json
import lzma
import unittest
from unittest.mock import patch
import p984g_apc_native_targets as n


class APCTargets(unittest.TestCase):
    def test_expected_unit_seed_normalization(self):
        v=n.base.h.load();subject=v['subjects']['target'];role='reset';s=subject['roles'][role]
        expected=next(c['result']['initial'] for c in v['cases'] if (c['graph'],c['role'])==('target',role))
        r=dict(C=s['C'],W_A=s['W_A'],Z=n.base.initial_z(subject,role),final=expected)
        with self.assertRaises(ValueError):n.base.h.bind_final(subject,role,r)
        r.update(C=list(map(float,s['C'])),W_A=list(map(float,s['W_A'])))
        n.base.h.bind_final(subject,role,r)

    def test_target_complete_points_and_mutations(self):
        oracle=n.base.h.check_retained();v=json.loads(lzma.decompress((n.ROOT/n.case_path('target','current')).read_bytes()))
        with patch.object(n.base,'execute',side_effect=AssertionError('native replay')):
            self.assertEqual(n.assess(v,oracle)['native_reads'],3)
        for change in (lambda b:b.update(ready_for_8_4h=True),
            lambda b:b['result']['reads']['final'].update(H=b['result']['reads']['current']['H']),
            lambda b:b['result']['after_W_A'].__setitem__(0,.75),
            lambda b:b['result']['after_Z']['entries'][0].__setitem__(2,123.),
            lambda b:b['result'].update(reset_unchanged=False),
            lambda b:b['result']['charge'].update(residual=1.)):
            bad=deepcopy(v);change(bad)
            with self.assertRaises(ValueError):n.assess(n.seal(bad),oracle)

    def test_combined_scope_and_preserved_history(self):
        v=n.summary();self.assertEqual((v['native_steps'],v['native_reads']),(4,12))
        self.assertTrue(v['native_prerequisites_complete']);self.assertFalse(v['user_accepted']);self.assertFalse(v['ready_for_8_4h'])
        self.assertEqual(len(v['historical_target_attempts']),2)
        self.assertTrue(all(r['native_steps']==0 for r in v['historical_target_attempts']))


if __name__=='__main__':unittest.main()
