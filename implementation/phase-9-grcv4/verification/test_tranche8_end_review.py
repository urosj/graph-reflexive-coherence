"""Pressure retained conclusions and exact ratio semantics without trajectories."""
from copy import deepcopy
import json
import lzma
from io import BytesIO
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import tranche8_end_review as review


class EndReviewTests(unittest.TestCase):
    def test_retained_scopes_and_zero_error_ratios(self):
        value=review.check()
        self.assertEqual(value['new_native_steps'],0)
        self.assertEqual(len(value['C_CI']['observations']),2)
        self.assertEqual(len(value['A_CI']['observations']),4)
        self.assertEqual(len(value['A_PC']['observations']),4)
        self.assertEqual(review.ratio(1,0)['kind'],'positive_effect_zero_error')
        self.assertEqual(review.ratio(0,0)['kind'],'zero_over_zero')
        self.assertEqual(review.ratio(3,2)['value'],'3/2')
        with self.assertRaises(ValueError):review.ratio(1,-1)

    def test_same_current_stale_geometry_cannot_inherit_aci_evidence(self):
        path=review.ROOT/review.BASE/'P9-8.4g-ACINativeSuccessor/source-current.json.xz'
        original=Path.read_bytes
        value=json.loads(lzma.decompress(original(path)))
        value['result']['roots']['current']['represented_geometry_digest']='wrong geometry'
        raw=lzma.compress(json.dumps(review.h.seal(value)).encode())
        def read(p):return raw if p==path else original(p)
        with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'full-point/native linkage'):
            review.mechanisms()

    def test_apc_margin_cannot_hide_matching_error(self):
        path=review.ROOT/review.BASE/'P9-8.4h-APC-current-1.json.xz'
        original=Path.read_bytes
        value=json.loads(lzma.decompress(original(path)))
        item=value['execution']['carrier_separation'];item['two_read_error_upper']=item['effect_lower']
        raw=lzma.compress(json.dumps(review.h.seal(value)).encode())
        def read(p):return raw if p==path else original(p)
        with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'inconsistent effect'):
            review.mechanisms()

    def test_selected_final_review_and_source_fail_closed(self):
        sys.path.insert(0,str(review.ROOT/review.h.handoff.SIDE/'tool/src'))
        from grcv4_explorer.tranche8_end import tranche8_end_reviews,tranche8_end_source,PINS
        value=tranche8_end_reviews(review.ROOT)
        self.assertEqual(value['families'],list(review.h.FAMILIES))
        self.assertTrue(value['final_review_user_accepted']);self.assertTrue(value['first_group_closed'])
        self.assertFalse(value['aggregate_closed'])
        with self.assertRaises(KeyError):tranche8_end_source(review.ROOT,'../outside')
        original=Path.read_bytes;path=review.ROOT/PINS['performance'][0]
        bad=json.loads(original(path));bad['new_cache_implementation']=True
        raw=json.dumps(review.h.seal(bad)).encode()
        def read(p):return raw if p==path else original(p)
        with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'changed final review'):
            tranche8_end_reviews(review.ROOT)

    def test_http_and_notebook_access(self):
        side=review.ROOT/review.h.handoff.SIDE/'tool'
        spec=importlib.util.spec_from_file_location('end_review_http',side/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        from urllib.parse import quote
        for route,expected in [('/tranche8-end.js',200),('/api/tranche8/end',200),
                ('/api/tranche8/end/source?path='+quote(review.RESULT),200),
                ('/api/tranche8/end?checkpoint=8.6&family=A_PC',404)]:
            handler=object.__new__(server.Handler);handler.path=route;handler.wfile=BytesIO()
            codes=[];handler.send_response=codes.append;handler.send_header=lambda *a:None;handler.end_headers=lambda:None
            with patch.object(server,'repository_root',return_value=review.ROOT):handler.do_GET()
            self.assertEqual(codes,[expected])
        notebook=json.loads((side/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(c for c in notebook['cells'] if c.get('id')=='tranche8-end-reviews')
        env={'repo_root':review.ROOT,'Path':Path}
        exec(compile(''.join(cell['source']),'<final review notebook>','exec'),env)
        self.assertEqual(env['tranche8_final']['families'],list(review.h.FAMILIES))


if __name__=='__main__':unittest.main()
