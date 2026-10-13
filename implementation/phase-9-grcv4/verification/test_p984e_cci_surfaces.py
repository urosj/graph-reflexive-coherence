"""Selected C_CI covariance stays producer-free, joint-root and scoped."""
import json
import sys
import unittest
from unittest.mock import patch

import p984e_cci as e
import tranche8_evidence as index

sys.path.insert(0,str(index.ROOT/index.SIDE/'tool/src'))
from grcv4_explorer import tranche8 as api


class JointCovarianceSurfaceTests(unittest.TestCase):
    def test_selected_api_and_browser_do_not_promote_or_execute(self):
        with (patch.object(api,'_index',return_value=index),
              patch.object(index,'checked',side_effect=AssertionError('full index')),
              patch.object(e.r,'CandidateCIRoot',side_effect=AssertionError('native root')),
              patch.object(e.r,'ProvisionalCandidateCIStep',side_effect=AssertionError('native step')),
              patch.object(e.certificate,'independent_certificate',side_effect=AssertionError('interval rerun'))):
            value=api.tranche8_status(index.ROOT,family='C_CI',checkpoint='8.4e')
        row=value['native']
        self.assertEqual((row['passing_pending_cells'],row['accepted_cells']),(0,20))
        self.assertTrue(row['full_joint_roots'])
        self.assertFalse(row['interval_certificates_rerun'])
        self.assertIsNotNone(row['acceptance'])
        self.assertFalse(value['other_families_checked'])
        saved=json.loads((index.ROOT/index.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(next(x for x in saved['coverage']['ordering_covariance']['family_results'] if x['family']=='C_CI'),row)
        for path in index.COVARIANCE_CCI_SOURCES:
            with patch.object(index.Sources,'current_bytes',return_value=b'forged'),self.assertRaisesRegex(ValueError,'source drift'):
                index.Sources(index.ROOT).raw(path)

    def test_cli_retained_only_dispatch(self):
        with patch.object(sys,'argv',['query','verify-retained','--family','C_CI','--checkpoint','8.4e','--recheck-numerics']),patch.object(index.subprocess,'run') as run:
            index.main();argv=run.call_args.args[0]
            self.assertTrue(argv[-3].endswith('p984e_cci.py'))
            self.assertEqual(argv[-2:],['check','--recheck-numerics'])
        import tranche8_retained as retained
        for mode in ('run','prepare'):
            with patch.object(sys,'argv',['retained',str(index.ROOT/e.SELF),mode]),self.assertRaisesRegex(ValueError,'retained-only'):
                retained.main()


if __name__=='__main__':unittest.main()
