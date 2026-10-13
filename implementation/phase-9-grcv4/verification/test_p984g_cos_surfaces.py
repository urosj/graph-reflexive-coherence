"""Larger prerequisites remain distinct from native admission on every surface."""
import json
from copy import deepcopy
import sys
import unittest
from unittest.mock import patch
import p984g_cos as p
import p984g_cos_bounds as bounds
import tranche8_evidence as index

sys.path.insert(0,str(index.ROOT/index.SIDE/'tool/src'))
from grcv4_explorer import tranche8 as api


class PrerequisiteSurfaces(unittest.TestCase):
    def test_storage_successor_is_one_exact_document_not_a_scientific_waiver(self):
        import prepare_p984c_boundaries as boundary
        retained=json.loads((index.ROOT/boundary.OUTPUT).read_text())
        current=deepcopy(retained)
        row=next(r for r in current['source_bindings'] if r['path']=='docs/reference/EvidenceStorage.md')
        row['sha256']='89e4728977ee45c8ea158179c3a5e7329fa5f45484c5df3e289c2ea3361f4a63'
        with patch.object(boundary,'build',return_value=deepcopy(current)):
            index.check_boundary_storage_successor(boundary,retained,index.ROOT)
        changed=deepcopy(current);changed['counts']['executed_cells']=1
        with patch.object(boundary,'build',return_value=changed),self.assertRaisesRegex(ValueError,'differs beyond'):
            index.check_boundary_storage_successor(boundary,retained,index.ROOT)

        import test_p984c_mechanics as mechanics
        original=mechanics.read(mechanics.RESULT);saved=deepcopy(original)
        index.check_mechanics_storage_successor(mechanics,original)
        self.assertEqual(saved,original)
        forged=deepcopy(original);forged['observations']['shared_layouts']=33
        with self.assertRaisesRegex(ValueError,'counts drift'):
            index.check_mechanics_storage_successor(mechanics,boundary.seal(forged))
        changed=deepcopy(current);changed['source_bindings'][1]['sha256']='0'*64
        with patch.object(boundary,'build',return_value=changed),self.assertRaisesRegex(ValueError,'differs beyond'):
            index.check_boundary_storage_successor(boundary,retained,index.ROOT)

    def test_selected_api_no_dense_or_native_producer(self):
        with patch.object(api,'_index',return_value=index), patch.object(p,'calculate',side_effect=AssertionError('dense rerun')), patch.object(bounds,'calculate',side_effect=AssertionError('interval rerun')):
            value=api.tranche8_status(index.ROOT,family='C_OS',checkpoint='8.4g')
        row=value['oracle']
        self.assertEqual(row['cases'],4)
        self.assertFalse(row['native_admission']);self.assertFalse(row['ready_for_8_4h'])
        self.assertTrue(row['user_accepted']);self.assertFalse(row['full_error_enclosure'])
        self.assertEqual(row['acceptance_scope'],'bounded_research_checkpoint_not_native_admission')
        self.assertTrue(row['pointwise_bounds']['user_accepted'])
        self.assertFalse(json.loads((index.ROOT/p.RESULTS).read_text())['user_accepted'])
        self.assertFalse(json.loads((index.ROOT/bounds.RESULTS).read_text())['user_accepted'])
        self.assertEqual(row['pointwise_bounds']['staged_positive'],4)
        self.assertEqual(row['pointwise_bounds']['exact_real_positive'],4)
        self.assertTrue(row['pointwise_bounds']['pointwise_resource_enclosures'])
        self.assertFalse(row['pointwise_bounds']['native_admission'])
        self.assertFalse(row['pointwise_bounds']['production_shortcut_integrated'])
        saved=json.loads((index.ROOT/index.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(saved['coverage']['larger_prerequisites']['family_results'][0],row)
        for name in (*index.LARGER_COS_SOURCES,*index.LARGER_COS_BOUNDS_SOURCES):
            with patch.object(index.Sources,'current_bytes',return_value=b'forged'),self.assertRaisesRegex(ValueError,'source drift'):
                index.Sources(index.ROOT).raw(name)
        with self.assertRaises(ValueError):index.family_status(index.ROOT,'A_PC','8.4g')

    def test_retained_dispatch_rejects_execution(self):
        with patch.object(sys,'argv',['query','verify-retained','--family','C_OS','--checkpoint','8.4g','--recheck-numerics']),patch.object(index.subprocess,'run') as run:
            index.main()
            self.assertEqual(run.call_args.args[0][-2:],['check','--recheck-numerics'])
            self.assertTrue(run.call_args.args[0][-3].endswith('p984g_cos_bounds.py'))
        import tranche8_retained as retained
        for mode in ('prepare','run-equations'):
            with patch.object(sys,'argv',['retained',str(index.ROOT/p.SELF),mode]),self.assertRaisesRegex(ValueError,'retained-only'):
                retained.main()
        for mode in ('prepare','run'):
            with patch.object(sys,'argv',['retained',str(index.ROOT/bounds.SELF),mode]),self.assertRaisesRegex(ValueError,'retained-only'):
                retained.main()


if __name__=='__main__':unittest.main()
