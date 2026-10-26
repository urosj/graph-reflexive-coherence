"""A_PC selected evidence, bounded credit and source access without solves."""
import json
import importlib.util
import io
import sys
import unittest
from unittest.mock import patch
import tranche8_evidence as index
import p984h_apc_campaign as c
import p984h_apc_covariance as cov

ASSET=index.SIDE+'tool/phase9-web/tranche8-apc-evidence.js'


class SurfaceTests(unittest.TestCase):
    def test_http_selected_routes_and_asset(self):
        script=index.ROOT/index.SIDE/'tool/scripts/serve_phase9.py'
        spec=importlib.util.spec_from_file_location('apc_phase9_server',script)
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        def request(url):
            handler=server.Handler.__new__(server.Handler);handler.path=url;handler.wfile=io.BytesIO()
            codes=[];handler.send_response=codes.append;handler.send_header=lambda *a:None;handler.end_headers=lambda:None
            handler.do_GET();return codes,handler.wfile.getvalue()
        with patch.object(server,'tranche8_status',return_value={'selected':True}) as status, \
                patch.object(server,'tranche8_source',return_value=(b'bound',{'sha256':'x','revision':None})) as source:
            self.assertEqual(request('/api/tranche8?family=A_PC&checkpoint=8.4h')[0],[200])
            self.assertEqual(status.call_args.kwargs,dict(family='A_PC',checkpoint='8.4h'))
            self.assertEqual(request('/api/tranche8/source?family=A_PC&checkpoint=8.4h&path=relative.json'),([200],b'bound'))
            self.assertEqual(source.call_args.kwargs,dict(family='A_PC',checkpoint='8.4h'))
            self.assertEqual(request('/tranche8-apc-evidence.js')[0],[200])
            for url in ('/api/tranche8?family=A_PC','/api/tranche8?family=A_PC&family=C_CI&checkpoint=8.4h','/api/tranche8?unknown=1'):
                status.reset_mock();self.assertEqual(request(url)[0],[404]);status.assert_not_called()

    def test_selected_api_and_projection_no_numerics(self):
        sys.path.insert(0,str(index.ROOT/index.SIDE/'tool/src'))
        from grcv4_explorer.tranche8 import tranche8_status
        with patch.object(c,'check',side_effect=AssertionError('full check forbidden')), \
                patch.object(c,'state',side_effect=AssertionError('reconstruction forbidden')), \
                patch.object(c.pc,'ProvisionalCandidatePCStep',side_effect=AssertionError('native forbidden')), \
                patch.object(c.p,'read',side_effect=AssertionError('interval solve forbidden')), \
                patch.object(cov,'subject',side_effect=AssertionError('transformed reconstruction forbidden')):
            value=tranche8_status(index.ROOT,family='A_PC',checkpoint='8.4h')
        row=value['runtime']
        self.assertEqual((row['native_steps'],row['total_native_events'],row['total_target_steps'],row['final_reads']),(1,9,36,2))
        self.assertTrue(row['continuation']['baseline_complete']);self.assertTrue(row['covariance']['covariance_complete'])
        self.assertTrue(row['unsigned_candidate_history']);self.assertTrue(row['full_PC_points'])
        self.assertTrue(row['explicit_carrier_loss_and_zero_target']);self.assertIsNotNone(row['retained_checkpoint_review'])
        self.assertTrue(row['user_accepted']);self.assertEqual(row['accepted_on'],'2026-10-26');self.assertFalse(row['aggregate_closed']);self.assertFalse(row['native_numerics_rerun'])
        self.assertFalse(value['other_families_checked'])
        saved=json.loads((index.ROOT/ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(value,saved);self.assertLess((index.ROOT/ASSET).stat().st_size,1000000)

    def test_missing_counterpart_restores_partial_status(self):
        pins=dict(index.LARGER_RUNTIME_APC_SOURCES);pins.pop(cov.path('reflect','reset'))
        pins.pop(c.BASE+'P9-8.4h-APCCloseout.json')
        with patch.object(index,'LARGER_RUNTIME_APC_SOURCES',pins):row=index.family_status(index.ROOT,'A_PC','8.4h')['runtime']
        self.assertFalse(row['covariance']['covariance_complete']);self.assertEqual(row['covariance']['target_steps'],15)
        self.assertFalse(row['user_accepted']);self.assertFalse(row['aggregate_closed'])

    def test_modified_pinned_evidence_fails_closed(self):
        with patch.object(index.Sources,'current_bytes',return_value=b'altered'),self.assertRaisesRegex(ValueError,'source drift'):
            index.family_status(index.ROOT,'A_PC','8.4h')


if __name__=='__main__':unittest.main()
