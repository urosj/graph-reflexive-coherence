"""Fifth-realization review, HTTP, browser, notebook and stale-source pressure."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import p9_aos_review as p

ROOT=p.b.ROOT
TOOL=ROOT/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool'
sys.path.insert(0,str(TOOL/'src'))
from grcv4_explorer import aos
from grcv4_explorer.phase9_verification import _profile_next_gate
from grcv4_explorer.tooling import managed_node,tool_environment


class AOSReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(p.large,'observe_step',side_effect=AssertionError('native rerun')):
            cls.record=p.checked()
            cls.status=aos.aos_status(ROOT)

    def test_scope_counts_and_resealed_mutations(self):
        self.assertEqual(self.status['realization_number'],5)
        self.assertEqual(_profile_next_gate(dict(aos_work=self.status)),self.status['next_work'])
        self.assertEqual(len(self.status['checkpoints']),16)
        for kind in ('acceptance','missing','cells','closure','exclusion','roster'):
            v=deepcopy(self.record)
            if kind=='acceptance':v['user_accepted']=True
            elif kind=='missing':v['checkpoints'].pop()
            elif kind=='cells':v['checkpoints'][0]['execution']['successful_history_cells']=42
            elif kind=='closure':v['full_GRC9V4_conformance']=True
            elif kind=='exclusion':v['original_large_reset_excluded']=False
            else:v['source_bindings']=[r for r in v['source_bindings'] if r['path']!=p.large.filename('step','reset',10)]
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.checked(value=p.b.seal(v))

    def test_source_drift_and_index_boundary(self):
        read=Path.read_bytes;target=ROOT/'src/pygrc/models/grc_9_v4_owner.py'
        with patch.object(Path,'read_bytes',lambda path:read(path)+b'# drift\n' if path==target else read(path)):
            with self.assertRaises(ValueError):aos.aos_status(ROOT)
        for name in ('../secret','src/../secret','/etc/passwd'):
            with self.subTest(name=name),self.assertRaises(KeyError):aos.aos_source(ROOT,name)
        raw,ref=aos.aos_source(ROOT,p.PATH)
        self.assertEqual(p.b.sha(raw),ref['sha256'])

    def test_fresh_checkout_restores_only_verified_aos_input(self):
        from scripts import evidence_storage as storage
        row=next(r for r in storage.entries(ROOT) if r['path']==p.deep.oracle.INPUTS)
        with TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ('scripts/evidence_storage.py',row['storage_path']):
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((ROOT/name).read_bytes())
            manifest=json.loads((ROOT/storage.MANIFEST).read_bytes());manifest['files']=[row]
            (root/storage.MANIFEST).write_text(json.dumps(manifest))
            self.assertFalse((root/row['path']).exists())
            aos.restore_inputs(root)
            self.assertEqual((root/row['path']).read_bytes(),(ROOT/row['path']).read_bytes())
            (root/row['path']).write_bytes(b'local drift')
            with self.assertRaises(ValueError):aos.restore_inputs(root)
            self.assertEqual((root/row['path']).read_bytes(),b'local drift')
        with patch.object(aos,'restore_inputs',wraps=aos.restore_inputs) as restore:
            self.assertEqual(aos.aos_status(ROOT),self.status)
            restore.assert_called_once_with(ROOT)

    def test_large_charge_and_geometry_binding_pressure(self):
        value=p.large.read('step')['execution']
        with p.large.policy():
            p.check_step_metadata(value)
            for field in ('charge','clock','geometry','sum'):
                bad=deepcopy(value)
                if field=='charge':bad['charge']['admitted_charge']+=1
                elif field=='clock':bad['after']['operation_id']='unowned-change'
                elif field=='geometry':bad['restart']['H_digest']='0'*64
                else:bad['exact_resource_sum_delta']='1'
                with self.subTest(field=field),self.assertRaises(ValueError):p.check_step_metadata(bad)

    def test_historical_sources_are_exact_git_bytes(self):
        h=p.historical;name='src/pygrc/models/grc_9_v4_owner.py'
        old=h.reference(ROOT,name)
        current=dict(path=name,sha256=h.sha((ROOT/name).read_bytes()))
        self.assertNotEqual(old,current)
        self.assertTrue(h.references_match(ROOT,[old],[current]))
        raw,ref=h.read_source(ROOT,old)
        self.assertEqual(raw,h.original(ROOT,name));self.assertEqual(ref['revision'],h.REVISION)
        bad=dict(current,sha256='0'*64)
        with self.assertRaises(ValueError):h.references_match(ROOT,[old],[bad])
        self.assertFalse(h.references_match(ROOT,[old],[current,dict(path='unregistered.py',sha256='0'*64)]))

    def test_http_and_real_notebook_cell(self):
        spec=importlib.util.spec_from_file_location('aos_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        def get(path):
            h=server.Handler.__new__(server.Handler);h.path,h.wfile=path,BytesIO();codes=[]
            h.send_response=codes.append;h.send_header=lambda *args:None;h.end_headers=lambda:None
            h.do_GET();return codes[-1],h.wfile.getvalue()
        code,raw=get('/api/aos');self.assertEqual(code,200);self.assertEqual(json.loads(raw),self.status)
        code,raw=get('/api/aos/source?path='+p.PATH)
        self.assertEqual(code,200);self.assertEqual(json.loads(raw),self.record)
        self.assertEqual(get('/api/aos?family=C_OS')[0],404)
        self.assertEqual(get('/api/aos/source?path=../secret')[0],404)
        code,raw=get('/aos.js');self.assertEqual(code,200);self.assertEqual(raw,(TOOL/'phase9-web/aos.js').read_bytes())
        with patch.object(server,'aos_status',side_effect=ValueError('source drift')):
            code,raw=get('/api/aos');self.assertEqual(code,503);self.assertEqual(set(json.loads(raw)),{'error'})
        book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(c for c in book['cells'] if c.get('id')=='query-aos')
        code=compile(''.join(cell['source']),'aos-notebook-cell','exec');namespace=dict(repo_root=ROOT)
        exec(code,namespace);self.assertEqual(namespace['phase9_aos'],self.status)
        with patch.object(aos,'aos_status',side_effect=ValueError('drift')):
            with self.assertRaises(ValueError):exec(code,namespace)
            self.assertIsNone(namespace['phase9_aos'])

    def test_browser_table_and_failure_clearing(self):
        script="""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const value=JSON.parse(readFileSync(0,'utf8'));
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let listener,ok=true;
function element(tag){return {tag,children:[],append(e){this.children.push(e)},insertCell(){const e=element('td');this.append(e);return e},insertRow(){const e=element('tr');this.append(e);return e},createTHead(){const e=element('thead');this.append(e);return e},createTBody(){const e=element('tbody');this.append(e);return e}};}
globalThis.document={getElementById(id){return id==='aos-refresh'?{addEventListener(_,fn){listener=fn}}:id==='aos-status'?status:output},createElement:element};
globalThis.fetch=async()=>({ok,json:async()=>value});
const {aosRows}=await import('./aos.js');
assert.equal(aosRows(value).length,16);
assert.throws(()=>aosRows({...value,user_accepted:true}));
await listener();assert.equal(output.children[0].tag,'table');assert.match(status.textContent,/review/);
ok=false;await listener();assert.equal(output.children.length,0);assert.match(status.textContent,/failed/);
const html=readFileSync('index.html','utf8');assert.match(html,/id="aos-refresh"/);assert.match(html,/A_OS/);
"""
        result=subprocess.run([str(managed_node()),'--input-type=module','-e',script],
            input=json.dumps(self.status),text=True,capture_output=True,cwd=TOOL/'phase9-web',
            timeout=30,env=tool_environment())
        self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':unittest.main()
