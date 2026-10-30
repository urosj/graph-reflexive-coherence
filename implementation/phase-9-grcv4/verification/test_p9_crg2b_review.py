from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import p9_crg2b_completion as c
import p9_crg2b_historical as history
import p9_crg2b_review as review
import p9_crg2b_section as section
import p9_crg2b_acceptance as acceptance

ROOT=c.ROOT
TOOL=ROOT/history.SIDE/'tool'
sys.path.insert(0,str(TOOL/'src'))
from grcv4_explorer import crg2b
from grcv4_explorer.tooling import managed_node, tool_environment


class ResearchSurfaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(c,'graph_certificate',side_effect=AssertionError('numeric rerun')), \
             patch.object(section,'certify',side_effect=AssertionError('numeric rerun')):
            cls.status=crg2b.crg2b_status(ROOT)

    def test_scope_and_source_drift(self):
        v=self.status
        self.assertEqual(v['graph_certificates'],54)
        self.assertEqual(len(v['prepared_sections']),4)
        self.assertTrue(all(r['section_passed'] and r['exact_real_first_step_positive'] for r in v['prepared_sections']))
        self.assertTrue(v['user_accepted']);self.assertEqual(v['research_native_steps'],0)
        real=Path.read_bytes;target=ROOT/c.SELF
        with patch.object(Path,'read_bytes',lambda p:real(p)+b'\n#drift' if p==target else real(p)):
            with self.assertRaises(ValueError):crg2b.crg2b_status(ROOT)

    def test_acceptance_preserves_execution_and_rejects_resealed_scope(self):
        import p9_crg2b_native_review as native
        v=acceptance.decision(ROOT)
        self.assertEqual(v['record_digest'],acceptance.DIGEST)
        self.assertFalse(native.checked(ROOT)['user_accepted'])
        self.assertTrue(self.status['bounded_scope_closed'])
        matrix=self.status['native_execution']['9.3']
        self.assertEqual(matrix['counts'],dict(bounded_accepted=36,passed_pending_acceptance=0,unselected_not_executed=4))
        self.assertEqual(matrix['execution_counts']['passed_pending_acceptance'],4)
        raw,ref=crg2b.crg2b_source(ROOT,acceptance.PATH)
        self.assertEqual(json.loads(raw),v)
        read=Path.read_bytes
        for key,new in [('aggregate_closed',True),('C1_regularity_debt','resolved'),
                        ('large_covariance_deferred_unexecuted',[]),('compatibility_counts',{'bounded_accepted':40})]:
            changed=native.b.seal(dict(v,**{key:new}))
            with self.subTest(key=key),patch.object(Path,'read_bytes',lambda p:json.dumps(changed).encode() if p==ROOT/acceptance.PATH else read(p)):
                with self.assertRaises(ValueError):acceptance.decision(ROOT)

    def test_native_scope_cannot_be_widened_by_resealing(self):
        import p9_crg2b_native_review as native
        target=ROOT/native.PATH;original=json.loads(target.read_bytes());real=Path.read_bytes
        for key,value in (("large_covariance_selected",["all"]),
                          ("large_covariance_deferred",[]),("stage","accepted"),
                          ("check_level","native_numerical_rerun")):
            changed=deepcopy(original);changed[key]=value;changed=native.b.seal(changed)
            with self.subTest(key=key),patch.object(Path,'read_bytes',lambda p:json.dumps(changed).encode() if p==target else real(p)):
                with self.assertRaises(ValueError):crg2b.crg2b_status(ROOT)

    def test_source_index_and_xz_are_exact(self):
        raw,ref=crg2b.crg2b_source(ROOT,section.RESULT)
        self.assertEqual(raw,(ROOT/section.RESULT).read_bytes())
        for name in ('../secret','/etc/passwd','unindexed-secret.py'):
            with self.assertRaises(KeyError):crg2b.crg2b_source(ROOT,name)

    def test_http_and_notebook_real_cell(self):
        spec=importlib.util.spec_from_file_location('crg2b_test_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        def get(path):
            h=server.Handler.__new__(server.Handler);h.path,h.wfile=path,BytesIO();codes=[]
            h.send_response=codes.append;h.send_header=lambda *args:None;h.end_headers=lambda:None
            h.do_GET();return codes[-1],h.wfile.getvalue()
        status,raw=get('/api/crg2b');self.assertEqual(status,200);self.assertEqual(json.loads(raw),self.status)
        self.assertEqual(get('/api/crg2b/source?path='+c.RESULT)[0],200)
        self.assertEqual(get('/crg2b.js')[0],200)
        for path in ('/api/crg2b?accepted=true','/api/crg2b/source?path=../secret',
                     '/api/crg2b/source?path=x&path=y'):
            self.assertEqual(get(path)[0],404)
        with patch.object(server,'crg2b_status',side_effect=ValueError('drift')):
            status,raw=get('/api/crg2b');self.assertEqual(status,503);self.assertEqual(set(json.loads(raw)),{'error'})
        book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(v for v in book['cells'] if v.get('id')=='query-crg2b')
        namespace=dict(repo_root=ROOT)
        code=compile(''.join(cell['source']),'query-crg2b','exec');exec(code,namespace)
        self.assertEqual(namespace['phase9_crg2b'],self.status)
        with patch.object(crg2b,'crg2b_status',side_effect=ValueError('drift')):
            with self.assertRaises(ValueError):exec(code,namespace)
        self.assertIsNone(namespace['phase9_crg2b'])

    def test_browser_scope_rejections(self):
        node=managed_node();module=(TOOL/'phase9-web/crg2b.js').as_uri()
        with patch.object(acceptance,'decision',return_value=None):pending=crg2b.crg2b_status(ROOT)
        script=f'''import {{crg2bRows}} from {json.dumps(module)};
const value = {json.dumps(self.status)};
if(crg2bRows(value).length !== 4) throw Error('missing rows');
const pending = {json.dumps(pending)};
if(crg2bRows(pending).length !== 4) throw Error('pending view lost');
let rejected=false;try{{crg2bRows({{...pending,user_accepted:true}})}}catch{{rejected=true}}
if(!rejected)throw Error('fabricated acceptance');
for(const edit of [v=>v.user_accepted=false,v=>v.acceptance.record_digest='0'.repeat(64),
 v=>v.native_execution['9.3'].counts.bounded_accepted=40,v=>v.aggregate_closed=true,
 v=>v.research_native_steps=1,v=>v.G3_support_added=['C_RG2b'],
 v=>v.prepared_sections.pop(),v=>v.prepared_sections.reverse(),v=>v.graph_certificates=53,
 v=>v.uniform_trajectory_enclosure=true,v=>v.large_covariance_deferred=[],v=>v.remaining_family=null]){{
 const v=structuredClone(value);edit(v);let rejected=false;
 try{{crg2bRows(v)}}catch{{rejected=true}}if(!rejected)throw Error('scope widened');
}}
console.log('CRG2B_BROWSER_PASS');'''
        result=subprocess.run([str(node),'--input-type=module','-e',script],cwd=TOOL,
                              env=tool_environment(),check=True,text=True,capture_output=True)
        self.assertIn('CRG2B_BROWSER_PASS',result.stdout)


class ResearchHistory(unittest.TestCase):
    def test_exact_successor_projection_and_unknown_hash(self):
        rows=history.epochs(ROOT)['sources']
        for name,row in rows.items():
            self.assertEqual(history.peel_sha(ROOT,name,row['after_sha256']),row['before_sha256'])
            self.assertEqual(history.peel_sha(ROOT,name,row['before_sha256']),row['before_sha256'])
            self.assertEqual(history.peel_sha(ROOT,name,'untrusted'),'untrusted')

    def test_live_drift_cannot_use_old_hash(self):
        name='implementation/Phase-9-GRCV4-Handoff.md';old=history.epochs(ROOT)['sources'][name]['before_sha256']
        real=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:real(p)+b'drift' if p==ROOT/name else real(p)):
            with self.assertRaises(ValueError):history.peel_sha(ROOT,name,old)

    def test_eighth_acceptance_preserved_and_current_priority(self):
        from p9_acipc_acceptance import epochs,record
        from p9_acipc_historical import epochs as execution_epochs
        from grcv4_explorer.phase9_verification import _profile_next_gate
        self.assertTrue(record(ROOT)['user_accepted']);self.assertTrue(epochs(ROOT));self.assertTrue(execution_epochs(ROOT))
        self.assertEqual(_profile_next_gate({'crg2b_work':dict(next_work='research'),'acipc_work':dict(next_work='accepted')}),'research')


if __name__=='__main__':unittest.main()
