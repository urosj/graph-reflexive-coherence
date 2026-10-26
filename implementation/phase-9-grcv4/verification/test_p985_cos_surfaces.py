"""Retained scope, drift, API/source and actual HTTP handler checks; no numerics."""
from copy import deepcopy
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import p985_cos as h
import p985_status as status


class COSSurfaceTests(unittest.TestCase):
    def test_retained_records(self):
        with status.cos_execution_epoch(h.ROOT):
            manifest,records=h.check()
            self.assertEqual(manifest,h.manifest())
        self.assertEqual(records['small']['observations']['tests'],8)
        self.assertEqual(records['large']['observations']['occupied_ports'],814)
        self.assertFalse(manifest['public_specialization_facade'])

    def test_selected_query_rejects_omitted_manifest_bindings(self):
        sys.path.insert(0,str(h.ROOT/h.SIDE/'tool/src'))
        from grcv4_explorer.tranche8 import tranche8_status
        original=Path.read_text
        value=json.loads((h.ROOT/h.INPUTS).read_text());value['source_bindings'].pop(h.TEST)
        raw=json.dumps(h.seal(value))
        def read(path,*a,**kw):return raw if path==h.ROOT/h.INPUTS else original(path,*a,**kw)
        with patch.object(Path,'read_text',read),self.assertRaisesRegex(ValueError,'complete frozen source roster'):
            status._view(h.ROOT,'C_OS')

    def test_resealed_coverage_and_scope_mutations_fail(self):
        original=Path.read_text
        for kind in ('omitted','reset','inconclusive','late','promotion','large'):
            name=h.result_path('large' if kind=='large' else 'small')
            value=json.loads((h.ROOT/name).read_text());v=deepcopy(value)
            if kind=='large':v['observations']['readmissions'].pop()
            elif kind=='promotion':v['user_accepted']=True
            elif kind=='omitted':v['observations']['cases'].pop('self_loop')
            elif kind=='reset':v['observations']['cases']['continuation_reset']['reset_baseline_preserved']=False
            elif kind=='inconclusive':v['observations']['cases']['reset_only_split']['bounded_outcome']='mathematical_rejection'
            else:v['observations']['cases']['publication_failures']['failures'].pop()
            raw=json.dumps(h.seal(v))
            def read(path,*a,**kw):return raw if path==h.ROOT/name else original(path,*a,**kw)
            with self.subTest(kind=kind),status.cos_execution_epoch(h.ROOT),patch.object(Path,'read_text',read),self.assertRaises((ValueError,KeyError)):
                h.check()

    def test_source_drift_rejects_without_numeric_retry(self):
        with status.cos_execution_epoch(h.ROOT):
            original=Path.read_bytes
            def read(path):return b'changed' if path==h.ROOT/h.TEST else original(path)
            with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'source drift'):
                h.check()

    def test_api_source_and_http_are_read_only_and_selected(self):
        sys.path.insert(0,str(h.ROOT/h.SIDE/'tool/src'))
        from grcv4_explorer.tranche8 import tranche8_status,tranche8_source
        with patch.object(h.native.GRC9V4COSOperation,'replay',side_effect=AssertionError('numerical replay forbidden')):
            status._view(h.ROOT,'C_OS')  # Direct worker logic also executes no numerics.
            value=tranche8_status(h.ROOT,family='C_OS',checkpoint='8.5')
            raw,ref=tranche8_source(h.ROOT,h.result_path('small'),family='C_OS',checkpoint='8.5')
            self.assertEqual(h.sha(raw),ref['sha256'])
            self.assertEqual(json.loads(raw),value['executions']['small'])
            self.assertTrue(value['user_accepted']);self.assertTrue(value['retained_integrity_only'])
            self.assertFalse(value['current_code_conformance_inferred'])
            for family in ('A_OS','C_PC','first_group'):
                with self.assertRaises(ValueError):tranche8_status(h.ROOT,family=family,checkpoint='8.5')
            for name in ('../outside','/absolute','specs/not-indexed.md'):
                with self.assertRaises(KeyError):tranche8_source(h.ROOT,name,family='C_OS',checkpoint='8.5')
            spec=importlib.util.spec_from_file_location('p985_http',h.ROOT/h.SIDE/'tool/scripts/serve_phase9.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            for route,expected in (
                ('/api/tranche8?family=C_OS&checkpoint=8.5',200),
                ('/api/tranche8?family=C_PC&checkpoint=8.5',503),
                ('/api/tranche8?family=C_OS&family=A_PC&checkpoint=8.5',404),
                ('/tranche8-lifecycle.js',200),
                ('/api/tranche8/source?family=C_OS&checkpoint=8.5&path='+h.REVIEW,200)):
                handler=object.__new__(module.Handler);handler.path=route;handler.wfile=BytesIO()
                codes=[];handler.send_response=codes.append;handler.send_header=lambda *args:None
                handler.end_headers=lambda:None
                with patch.object(module,'repository_root',return_value=h.ROOT):handler.do_GET()
                self.assertEqual(codes,[expected],route)
                self.assertTrue(handler.wfile.getvalue())


if __name__=='__main__':unittest.main()
