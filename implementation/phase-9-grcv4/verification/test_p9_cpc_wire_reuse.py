"""Byte-exact research memo pressure; identities and rejections cannot change."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import p9_cpc_wire_reuse as w

class WireReuseTests(unittest.TestCase):
    def test_exact_bytes_mutation_and_float_boundaries(self):
        values=[{'matrix':[[0.,1.,2**-1074,1e20,2**53*1.,'\U00010000','\ue000']]*1800},
                {'nested':[True,None,1,1.0,1e-7,1e21]*5000}]
        expected=[w.codec.canonical_json_bytes(v) for v in values]
        with w.wire_reuse() as stats:
            for v,raw in zip(values,expected,strict=True):
                self.assertEqual(w.codec.canonical_json_bytes(v),raw)
                self.assertEqual(w.codec.canonical_json_bytes(deepcopy(v)),raw)
            self.assertGreaterEqual(stats['hits'],2)
            changed=deepcopy(values[0]);changed['matrix'][0][1]=3.
            self.assertNotEqual(w.codec.canonical_json_bytes(changed),expected[0])
        self.assertEqual(stats['retained_bytes'],0)
    def test_failed_input_is_never_reused(self):
        valid={'rows':[[1.]*100]*200}
        with w.wire_reuse() as stats:
            w.codec.canonical_json_bytes(valid);w.codec.canonical_json_bytes(valid)
            for bad in ({1:valid},{'rows':[float('nan')]},{'rows':[-0.]},{'rows':[2**53]}, {'rows':['\ud800']}):
                with self.subTest(bad=repr(bad)[:60]),self.assertRaises((ValueError,TypeError)):
                    w.codec.canonical_json_bytes(bad)
            self.assertFalse(stats['failed_results_cached'])
    def test_entry_and_aggregate_limits_and_nested_cleanup(self):
        original=w.codec._dependency
        with patch.object(w,'MIN_BYTES',1),patch.object(w,'MAX_ENTRIES',2),patch.object(w,'TOTAL_BYTES',100):
            with w.wire_reuse() as stats:
                with w.wire_reuse() as nested:self.assertIs(stats,nested)
                for i in range(12):w.codec.canonical_json_bytes({'i':i,'data':'x'*10})
                self.assertGreater(stats['evictions'],0);self.assertLessEqual(stats['retained_bytes'],100)
            self.assertIs(w.codec._dependency,original);self.assertEqual(stats['retained_bytes'],0)
    def test_canonical_decoder_rejects_noncanonical_bytes_after_hit(self):
        value={'rows':[1.]*40000};raw=w.codec.canonical_json_bytes(value)
        with w.wire_reuse() as stats:
            self.assertEqual(w.codec.canonical_json_bytes(w.codec.decode_canonical_json(raw)),raw)
            for bad in (raw+b' ',raw.replace(b'1',b'1.0',1),b'{"x":1,"x":1}'):
                with self.assertRaises(ValueError):w.codec.decode_canonical_json(bad)
            self.assertGreater(stats['hits'],0)

if __name__=='__main__':unittest.main()
