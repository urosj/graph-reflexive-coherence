"""Read-only retained parity and predecessor checks; no numerical rerun."""
import json
import lzma
import unittest
from unittest.mock import patch

import p984h_cos_dyadic_rounding as read_probe
import p984h_cos_dyadic_step as step_probe
import p984h_pre_solve_reuse_sources as history

run = read_probe.run


class DyadicEvidence(unittest.TestCase):
    def test_fresh_read_and_changing_step_have_exact_predecessor_parity(self):
        baseline=json.loads(lzma.decompress((run.ROOT/read_probe.kernel.probe.OUTPUT).read_bytes()))
        read=json.loads(lzma.decompress((run.ROOT/read_probe.OUTPUT).read_bytes()))
        step=json.loads(lzma.decompress((run.ROOT/step_probe.OUTPUT).read_bytes()))
        prefix=run.read('prefix')
        for record in (baseline,read,step,prefix):
            self.assertEqual(record,run.seal(record))
        self.assertEqual(read['baseline_record_digest'],baseline['record_digest'])
        self.assertEqual(read['input_digest'],baseline['input_digest'])
        expected=run.digest({k:baseline[k] for k in read_probe.kernel.previous.FIELDS})
        self.assertEqual(read['scientific_view_digest'],expected)
        self.assertTrue(read['baseline_parity'])
        self.assertEqual(baseline['prefix_digest'],prefix['record_digest'])
        self.assertEqual(step['prefix_record_digest'],prefix['record_digest'])
        source=prefix['execution']['steps'][1]
        self.assertEqual(step['scientific_view_digest'],run.digest(
            {k:v for k,v in source.items() if k not in ('seconds','dense_errors','trigger')}))
        self.assertTrue(step['whole_step_parity'])
        self.assertEqual((step['native_steps'],step['native_events'],step['new_campaign_steps']),(1,0,0))
        self.assertEqual((read['native_steps'],read['native_events']),(0,0))
        for record in (read,step):
            for name,sha in record['source_bindings'].items():
                with self.subTest(name=name):self.assertEqual(run.oracle.sha(name),sha)

    def test_uncommitted_predecessors_are_pinned_bytes_not_source_waivers(self):
        for name,digest,archive_key in (
            ('src/pygrc/models/grc_v4_certification.py',history.SCALAR_PREDECESSOR_SOURCE_SHA,'SCALAR_PREDECESSOR_ARCHIVE_SHA'),
            ('specs/grc-v4-numerical-policy.md',history.SPEC_PREDECESSOR_SOURCE_SHA,'SPEC_PREDECESSOR_ARCHIVE_SHA'),
        ):
            self.assertTrue(history.historical_binding(name,digest,b'new implementation'))
            self.assertFalse(history.historical_binding(name,'forged',b'new implementation'))
            with patch.object(history,archive_key,'0'*64):
                self.assertFalse(history.historical_binding(name,digest,b'new implementation'))


if __name__=='__main__':unittest.main()
