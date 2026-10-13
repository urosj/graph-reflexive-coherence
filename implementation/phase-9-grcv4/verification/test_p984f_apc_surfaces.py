"""A_PC scoped views preserve history semantics and scoped acceptance."""
import json
import sys
import unittest
from unittest.mock import patch
import p984f_apc as e
import tranche8_evidence as index
sys.path.insert(0,str(index.ROOT/index.SIDE/'tool/src'))
from grcv4_explorer import tranche8 as api


class ASurfaceTests(unittest.TestCase):
    def test_selected_family_uses_no_native_or_interval_producer(self):
        with (patch.object(api,'_index',return_value=index),
              patch.object(index,'checked',side_effect=AssertionError('full index')),
              patch.object(e.r,'CandidatePCRead',side_effect=AssertionError('native root')),
              patch.object(e.r,'ProvisionalCandidatePCStep',side_effect=AssertionError('native step')),
              patch.object(e.r,'independent_certificate',side_effect=AssertionError('interval rerun'))):
            value=api.tranche8_status(index.ROOT,family='A_PC',checkpoint='8.4f')
        row=value['native']
        self.assertEqual((row['passing_pending_cells'],row['accepted_cells']),(0,24))
        self.assertFalse(row['full_joint_roots']);self.assertTrue(row['persistent_carrier']);self.assertTrue(row['unsigned_candidate_history'])
        self.assertFalse(row['interval_certificates_rerun']);self.assertIsNotNone(row['acceptance'])
        saved=json.loads((index.ROOT/index.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(next(x for x in saved['coverage']['chart_covariance']['family_results'] if x['family']=='A_PC'),row)
        for path in index.CHART_APC_SOURCES:
            with patch.object(index.Sources,'current_bytes',return_value=b'forged'),self.assertRaisesRegex(ValueError,'source drift'):
                index.Sources(index.ROOT).raw(path)

    def test_retained_dispatch_forbids_native_modes(self):
        with patch.object(sys,'argv',['query','verify-retained','--family','A_PC','--checkpoint','8.4f','--recheck-numerics']),patch.object(index.subprocess,'run') as run:
            index.main();argv=run.call_args.args[0]
            self.assertTrue(argv[-3].endswith('p984f_apc.py'));self.assertEqual(argv[-2:],['check','--recheck-numerics'])
        import tranche8_retained as retained
        for mode in ('run','prepare'):
            with patch.object(sys,'argv',['retained',str(index.ROOT/e.SELF),mode]),self.assertRaisesRegex(ValueError,'retained-only'):
                retained.main()


if __name__=='__main__':unittest.main()
