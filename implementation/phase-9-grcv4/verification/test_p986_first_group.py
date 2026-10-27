"""Pressure the conformance boundary, exact subjects and portable selected views."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import p986_first_group as h


class ConformanceTests(unittest.TestCase):
    def test_retained_decision_and_honest_counts(self):
        v=h.check()
        self.assertEqual([r['family'] for r in v['families']],list(h.FAMILIES))
        self.assertEqual(v['counts']['prior_8_5_small_tests'],26)
        self.assertEqual(v['counts']['prior_8_4_target_steps'],144)
        self.assertEqual(v['counts']['new_native_steps'],0)
        self.assertFalse(v['user_accepted']);self.assertFalse(v['aggregate_closed'])
        self.assertEqual(len(v['remaining_families']),6)

    def test_resealed_domain_history_horizon_and_scope_widening_fail(self):
        shared=h.check_shared(h.ROOT);old=h.load(h.ROOT,h.handoff.RESULT);acceptance=h.load(h.ROOT,h.ACCEPTANCE)
        cases=[('C_OS','profile'),('C_CI','reset'),('A_CI','horizon'),('A_PC','mechanism'),
               ('A_PC','graph'),('C_CI','universal'),('C_OS','lifecycle'),('A_CI','acceptance')]
        for family,kind in cases:
            v=h.load(h.ROOT,h.path(family))
            if kind=='profile':v['exact_domain']['profiles']['state']='wrong-profile'
            elif kind=='reset':v['exact_domain'].pop('target_reset_digest')
            elif kind=='horizon':v['exact_domain']['mapped_horizon_per_role']=10
            elif kind=='mechanism':v['scientific_scope']['limitation']='uniform carrier margin'
            elif kind=='graph':v['exact_domain']['graphs']['state']['vertices']=400
            elif kind=='universal':v['limits']['arbitrary_graph_numerical_admission']=True
            elif kind=='lifecycle':v['lifecycle_8_5']['execution_digests']['large']='0'*64
            else:v['user_accepted']=True
            with self.subTest(family=family,kind=kind),self.assertRaises((ValueError,KeyError)):
                h.validate_family(h.seal(v),old,shared,acceptance)

    def test_missing_family_and_changed_source_fail(self):
        original=Path.read_bytes
        def missing(path):
            if path==h.ROOT/h.path('A_PC'):raise FileNotFoundError('missing family')
            return original(path)
        with patch.object(Path,'read_bytes',missing),self.assertRaises(FileNotFoundError):h.assemble(h.ROOT)
        v=h.load(h.ROOT,h.RESULT)
        ref=next(r for r in v['source_refs'] if r['path']=='src/pygrc/models/grc_v4_lifecycle.py' and not r.get('revision'))
        with patch.object(Path,'read_bytes',return_value=b'changed'),self.assertRaisesRegex(ValueError,'source drift'):
            h.handoff.authenticate(h.ROOT,ref)

    def test_selected_api_and_ambiguous_epoch_access(self):
        sys.path.insert(0,str(h.ROOT/h.handoff.SIDE/'tool/src'))
        from grcv4_explorer.tranche8 import tranche8_status,tranche8_source
        with patch.object(h,'review_family',side_effect=AssertionError('do not rerun review workers')):
            with ThreadPoolExecutor(max_workers=5) as pool:
                views=list(pool.map(lambda f:tranche8_status(h.ROOT,family=f,checkpoint='8.6'),('first_group',*h.FAMILIES)))
        self.assertEqual([v['family'] for v in views],['first_group',*h.FAMILIES])
        self.assertTrue(all(not v['numerical_trajectories_rerun'] for v in views))
        self.assertTrue(all(v['user_accepted'] and v['first_group_closed'] for v in views))
        source='src/pygrc/models/grc_v4_lifecycle.py'
        with self.assertRaisesRegex(KeyError,'multiple execution epochs'):
            tranche8_source(h.ROOT,source,family='first_group',checkpoint='8.6')
        for family in ('C_OS','A_CI'):
            raw,ref=tranche8_source(h.ROOT,source,family=family,checkpoint='8.6')
            self.assertEqual(h.sha(raw),ref['sha256'])
            self.assertEqual(ref.get('revision'),'5b8a432e' if family=='C_OS' else None)
        with self.assertRaises(KeyError):tranche8_source(h.ROOT,'../outside',family='C_CI',checkpoint='8.6')
        with self.assertRaises(ValueError):tranche8_status(h.ROOT,family='C_PC',checkpoint='8.6')

    def test_acceptance_rejects_changed_or_unpinned_records(self):
        import p986_acceptance as acceptance
        value=h.status(); record=h.load(h.ROOT,acceptance.ACCEPTANCE)
        self.assertTrue(acceptance.accepted(value,record)['user_accepted'])
        for key,new in [('aggregate_closed',True),('decision_digest','wrong')]:
            changed=dict(record);changed[key]=new
            with self.assertRaises(ValueError):acceptance.accepted(value,h.seal(changed))

    def test_http_and_notebook_surface(self):
        spec=importlib.util.spec_from_file_location('p986_http',h.ROOT/h.handoff.SIDE/'tool/scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        for route in ('/tranche8-conformance.js','/api/tranche8?family=first_group&checkpoint=8.6'):
            handler=object.__new__(server.Handler);handler.path=route;handler.wfile=BytesIO()
            codes=[];handler.send_response=codes.append;handler.send_header=lambda *a:None;handler.end_headers=lambda:None
            with patch.object(server,'repository_root',return_value=h.ROOT):handler.do_GET()
            self.assertEqual(codes,[200])
        notebook=json.loads((h.ROOT/h.handoff.SIDE/'tool/notebooks/phase9_verification.ipynb').read_text())
        for cell in notebook['cells']:
            if cell['cell_type']=='code':compile(''.join(cell['source']),'<notebook>','exec')


if __name__=='__main__':unittest.main()
