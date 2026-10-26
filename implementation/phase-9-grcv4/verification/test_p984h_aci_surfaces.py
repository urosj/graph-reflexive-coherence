"""Selected A_CI projection: pinned coverage without native reconstruction."""
import json
import importlib.util
import io
import sys
import unittest
from unittest.mock import patch
import tranche8_evidence as index
import p984h_aci_campaign as c
import p984h_aci_covariance as cov


class SurfaceTests(unittest.TestCase):
    def test_http_selected_routes_and_query_rejection(self):
        script=index.ROOT/index.SIDE/'tool/scripts/serve_phase9.py'
        spec=importlib.util.spec_from_file_location('aci_phase9_server',script)
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        def request(url):
            handler=server.Handler.__new__(server.Handler);handler.path=url;handler.wfile=io.BytesIO()
            codes=[];handler.send_response=codes.append;handler.send_header=lambda *a:None;handler.end_headers=lambda:None
            handler.do_GET();return codes,handler.wfile.getvalue()
        with patch.object(server,'tranche8_status',return_value={'selected':True}) as status, \
                patch.object(server,'tranche8_source',return_value=(b'bound',{'sha256':'x','revision':None})) as source:
            self.assertEqual(request('/api/tranche8?family=A_CI&checkpoint=8.4h')[0],[200])
            self.assertEqual(status.call_args.kwargs,dict(family='A_CI',checkpoint='8.4h'))
            self.assertEqual(request('/api/tranche8/source?family=A_CI&checkpoint=8.4h&path=relative.json'),([200],b'bound'))
            self.assertEqual(source.call_args.kwargs,dict(family='A_CI',checkpoint='8.4h'))
            for url in ('/api/tranche8?family=A_CI','/api/tranche8?family=A_CI&family=C_CI&checkpoint=8.4h',
                        '/api/tranche8?unknown=1'):
                status.reset_mock();self.assertEqual(request(url)[0],[404]);status.assert_not_called()

    def test_selected_source_uses_family_index_not_full_index(self):
        side=index.ROOT/index.SIDE/'tool/src';sys.path.insert(0,str(side))
        from grcv4_explorer import tranche8
        from types import SimpleNamespace
        name='relative.json';ref=dict(path=name,sha256='x',revision=None,basis='pinned')
        class Sources:
            def __init__(self,root):self.refs={}
            def raw(self,path,historical=False):self.refs[path]=ref;return b'bound'
        from unittest.mock import Mock
        selected=Mock(return_value={'source_refs':[ref]});full=Mock(side_effect=AssertionError('full index forbidden'))
        module=SimpleNamespace(family_status=selected,checked=full,Sources=Sources,require=c.require)
        with patch.object(tranche8,'_index',return_value=module):
            self.assertEqual(tranche8.tranche8_source(index.ROOT,name,family='A_CI',checkpoint='8.4h'),(b'bound',ref))
            with self.assertRaises(KeyError):tranche8.tranche8_source(index.ROOT,'unindexed',family='A_CI',checkpoint='8.4h')
        full.assert_not_called()

    def test_selected_api_and_generated_browser_no_numerics(self):
        side=index.ROOT/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src'
        sys.path.insert(0,str(side))
        from grcv4_explorer.tranche8 import tranche8_status
        with patch.object(c,'check',side_effect=AssertionError('full check forbidden')), \
                patch.object(c,'state',side_effect=AssertionError('reconstruction forbidden')), \
                patch.object(c.ci,'CandidateCIRoot',side_effect=AssertionError('native forbidden')), \
                patch.object(c.oracle,'analyze',side_effect=AssertionError('interval solve forbidden')), \
                patch.object(cov,'subject',side_effect=AssertionError('transformed reconstruction forbidden')):
            value=tranche8_status(index.ROOT,family='A_CI',checkpoint='8.4h')
        row=value['runtime']
        self.assertEqual((row['native_steps'],row['total_native_events'],row['total_target_steps'],row['final_reads']),(1,9,36,2))
        self.assertTrue(row['continuation']['baseline_complete']);self.assertTrue(row['covariance']['covariance_complete'])
        self.assertTrue(row['unsigned_candidate_history']);self.assertTrue(row['full_joint_roots'])
        self.assertIsNotNone(row['retained_checkpoint_review'])
        self.assertIsNotNone(row['charge_checker_successor'])
        self.assertEqual(row['continuation']['roles']['current']['steps'][7]['represented_charge']['residual'],2**-45)
        self.assertTrue(row['user_accepted']);self.assertEqual(row['accepted_on'],'2026-10-26')
        self.assertTrue(row['original_execution_flags_unchanged'])
        self.assertFalse(row['aggregate_closed']);self.assertFalse(row['native_numerics_rerun'])
        self.assertFalse(value['other_families_checked'])
        saved=json.loads((index.ROOT/index.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(row,next(x for x in saved['coverage']['larger_runtime'] if x['family']=='A_CI'))

    def test_missing_counterpart_restores_partial_status(self):
        pins=dict(index.LARGER_RUNTIME_ACI_SOURCES);pins.pop(cov.path('reflect','reset'))
        pins.pop(c.BASE+'P9-8.4h-ACICloseout.json')
        with patch.object(index,'LARGER_RUNTIME_ACI_SOURCES',pins):
            row=index.family_status(index.ROOT,'A_CI','8.4h')['runtime']
        self.assertFalse(row['covariance']['covariance_complete']);self.assertEqual(row['covariance']['target_steps'],15)
        self.assertFalse(row['user_accepted']);self.assertFalse(row['aggregate_closed'])

    def test_modified_pinned_evidence_fails_closed(self):
        with patch.object(index.Sources,'current_bytes',return_value=b'altered'), self.assertRaisesRegex(ValueError,'source drift'):
            index.family_status(index.ROOT,'A_CI','8.4h')


if __name__=='__main__':unittest.main()
