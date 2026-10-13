"""Selected API/CLI/browser evidence stays scoped and producer-free."""
import json
import sys
import unittest
from unittest.mock import patch

import p984e_cos as e
import tranche8_evidence as index

sys.path.insert(0,str(index.ROOT/index.SIDE/'tool/src'))
from grcv4_explorer import tranche8 as api


class CovarianceSurfaceTests(unittest.TestCase):
    def test_selected_scope_pins_and_browser(self):
        with (patch.object(api,'_index',return_value=index),patch.object(index,'checked',side_effect=AssertionError('full index')),
            patch.object(e.b,'ProvisionalCandidateCOSStep',side_effect=AssertionError('native rerun')),
            patch.object(e.b,'dense_os',side_effect=AssertionError('dense rerun'))):
            v=api.tranche8_status(index.ROOT,family='C_OS',checkpoint='8.4e')
        self.assertEqual(v['native']['passing_pending_cells'],0)
        self.assertEqual(v['native']['accepted_cells'],20)
        self.assertFalse(v['native']['dense_comparisons_rerun'])
        saved=json.loads((index.ROOT/index.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(next(r for r in saved['coverage']['ordering_covariance']['family_results'] if r['family']=='C_OS'),v['native'])
        for path in index.COVARIANCE_COS_SOURCES:
            with patch.object(index.Sources,'current_bytes',return_value=b'forged'),self.assertRaisesRegex(ValueError,'source drift'):
                index.Sources(index.ROOT).raw(path)
        with self.assertRaisesRegex(ValueError,'not executed'):index.family_status(index.ROOT,'A_PC','8.4e')

    def test_retained_dispatch_and_no_execution_modes(self):
        with patch.object(sys,'argv',['query','verify-retained','--family','C_OS','--checkpoint','8.4e','--recheck-numerics']),patch.object(index.subprocess,'run') as run:
            index.main()
            argv=run.call_args.args[0]
            self.assertTrue(argv[-3].endswith('p984e_cos.py'))
            self.assertEqual(argv[-2:],['check','--recheck-numerics'])
        import tranche8_retained as retained
        for mode in ('run','prepare'):
            with patch.object(sys,'argv',['retained',str(index.ROOT/e.SELF),mode]),self.assertRaisesRegex(ValueError,'retained-only'):
                retained.main()


if __name__=='__main__':unittest.main()
