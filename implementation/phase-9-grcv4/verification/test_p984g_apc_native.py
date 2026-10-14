"""Retained complete-point, two-writer, charge and authority pressure."""
from copy import deepcopy
import json
import lzma
import unittest
from unittest.mock import patch
import p984g_apc_native as n


class APCNative(unittest.TestCase):
    def test_retained_source_and_resealed_mutations(self):
        oracle=n.h.check_retained()
        v=json.loads(lzma.decompress((n.ROOT/n.case_path('source','current')).read_bytes()))
        with patch.object(n,'execute',side_effect=AssertionError('native replay')),patch.object(n.p,'analyze',side_effect=AssertionError('oracle replay')):
            row=n.assess(v,oracle)
        self.assertEqual(row['native_reads'],3);self.assertTrue(row['full_point_parity'])
        mutations=[lambda x:x.update(native_events=1),lambda x:x.update(ready_for_8_4h=True),
            lambda x:x['result'].update(reset_unchanged=False),lambda x:x['result'].update(carrier_writes=0),
            lambda x:x['result']['charge'].update(admitted_charge=201.),
            lambda x:x['result'].update(exact_stored_charge_drift='0'),
            lambda x:x['result']['after_W_A'].__setitem__(0,.75),
            lambda x:x['result']['after_C'].__setitem__(0,1.25),
            lambda x:x['result']['reads']['final'].update(H=x['result']['reads']['current']['H']),
            lambda x:x['result']['reads']['final']['flat'].__setitem__(0,123.),
            lambda x:x['result']['reads']['reset']['certificate'].update(source_norm_upper='999999')]
        for i,mutate in enumerate(mutations):
            bad=deepcopy(v);mutate(bad)
            with self.subTest(i=i),self.assertRaises(ValueError):n.assess(n.seal(bad),oracle)

    def test_historical_two_source_successes_and_two_checker_failures(self):
        v=n.summary();self.assertEqual(v['native_steps'],2);self.assertEqual(v['native_reads'],6)
        self.assertFalse(v['native_prerequisites_complete']);self.assertFalse(v['ready_for_8_4h']);self.assertFalse(v['user_accepted'])
        self.assertTrue(all(c['error']['message']=='final point not bound to C/W/Z/read fields' for c in v['cases'] if c['graph']=='target'))
        self.assertEqual(v['native_events'],0);self.assertEqual(v['committed_steps'],0)


if __name__=='__main__':unittest.main()
