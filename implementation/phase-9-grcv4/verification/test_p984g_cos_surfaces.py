"""Larger prerequisites remain distinct from native admission on every surface."""
import json
from copy import deepcopy
import sys
import unittest
from unittest.mock import patch
import p984g_cos as p
import p984g_cos_bounds as bounds
import p984g_cos_native as native
import tranche8_evidence as index

sys.path.insert(0,str(index.ROOT/index.SIDE/'tool/src'))
from grcv4_explorer import tranche8 as api


class PrerequisiteSurfaces(unittest.TestCase):
    def test_frozen_preflight_registers_review_before_scientific_validation(self):
        import p984d_apc_runtime as deep

        class ReachedScientificChecker(Exception):
            pass

        # Exercise the real projection wiring, stopping before the expensive
        # historical checker: this test covers references, not its numerics.
        sources=index.Sources(index.ROOT)
        with patch.object(deep,'status',side_effect=ReachedScientificChecker), self.assertRaises(ReachedScientificChecker):
            index.deep_family_view(sources,'A_PC')
        self.assertEqual(set(sources.refs),{deep.INPUTS,deep.RESULTS,deep.REVIEW})
        saved=json.loads((index.ROOT/index.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        refs={r['path']:r for r in saved['source_refs']}
        self.assertEqual(sources.refs,{p:refs[p] for p in sources.refs})

        # Restoring the reference must authenticate it, not silently trust the
        # browser's existing catalog or merely insert a path into the output.
        original=index.Sources.current_bytes
        def altered(source,name):
            return b'forged review' if name==deep.REVIEW else original(source,name)
        with patch.object(index.Sources,'current_bytes',altered), patch.object(deep,'status') as scientific:
            with self.assertRaisesRegex(ValueError,'source drift'):
                index.deep_family_view(index.Sources(index.ROOT),'A_PC')
            scientific.assert_not_called()

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
        changed=deepcopy(original)
        next(r for r in changed['source_bindings'] if r['path'].startswith('src/'))['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'historical mechanical runtime bindings drift'):
            index.check_mechanics_storage_successor(mechanics,boundary.seal(changed))
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
        successor=row['native_prerequisites']
        self.assertTrue(successor['production_shortcut_integrated'])
        self.assertTrue(successor['native_admission'])
        self.assertEqual(successor['numerical_steps'],4)
        self.assertEqual(successor['committed_steps'],0)
        self.assertEqual(successor['native_events'],0)
        self.assertTrue(successor['user_accepted'])
        self.assertTrue(successor['ready_for_8_4h'])
        self.assertFalse(native.read(native.RESULTS)['user_accepted'])
        self.assertIn('acceptance',successor)
        self.assertTrue(successor['scientifically_ready_for_8_4h'])
        saved=json.loads((index.ROOT/index.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(saved['coverage']['larger_prerequisites']['family_results'][0],row)
        for name in (*index.LARGER_COS_SOURCES,*index.LARGER_COS_BOUNDS_SOURCES,*index.LARGER_COS_NATIVE_SOURCES):
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
        for options in (['prepare'],['run-case'],['summarize'],['check','--recheck-numerics']):
            with patch.object(sys,'argv',['retained',str(index.ROOT/native.SELF),*options]),self.assertRaisesRegex(ValueError,'retained-only'):
                retained.main()

    def test_default_retained_dispatch_selects_native_successor(self):
        with patch.object(sys,'argv',['query','verify-retained','--family','C_OS','--checkpoint','8.4g']),patch.object(index.subprocess,'run') as run:
            index.main()
            self.assertEqual(run.call_args.args[0][-1],'check')
            self.assertTrue(run.call_args.args[0][-2].endswith('p984g_cos_native.py'))

    def test_historical_adapter_keeps_old_bindings_and_science(self):
        original=p.make_manifest
        retained=p.read(p.INPUTS)
        self.assertNotEqual(original(),retained)
        with index.historical_larger_sources():
            self.assertEqual(p.make_manifest(),retained)
            forged=deepcopy(p.read(p.RESULTS));forged['native_admission']=True
            with self.assertRaisesRegex(ValueError,'scope'):
                p.check(retained,p.seal(forged))
        self.assertIs(p.make_manifest,original)


if __name__=='__main__':unittest.main()
