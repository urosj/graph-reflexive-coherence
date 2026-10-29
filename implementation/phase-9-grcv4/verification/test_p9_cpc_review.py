"""C_PC read-only evidence: exact scope, HTTP, browser, notebook and source drift."""
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
import p9_cpc_review as p

ROOT=p.b.ROOT
TOOL=ROOT/p.historical.SIDE
sys.path.insert(0,str(TOOL/'src'))
from grcv4_explorer import cpc
from grcv4_explorer.phase9_verification import _profile_next_gate
from grcv4_explorer.tooling import managed_node,tool_environment


class CPCReviewTests(unittest.TestCase):
    def setUp(self):
        pending=patch('p9_cpc_acceptance.decision',return_value=None)
        pending.start();self.addCleanup(pending.stop)

    @classmethod
    def setUpClass(cls):
        with patch.object(p.large,'observe_step',side_effect=AssertionError('native rerun')), \
                patch('p9_cpc_acceptance.decision',return_value=None):
            cls.record=p.checked();cls.status=cpc.cpc_status(ROOT)

    def test_scope_counts_and_resealed_mutations(self):
        self.assertEqual(self.status['realization_number'],6)
        self.assertEqual(_profile_next_gate(dict(cpc_work=self.status)),self.status['next_work'])
        self.assertEqual(len(self.status['checkpoints']),16)
        for kind in ('acceptance','missing','cells','closure','exclusion','roster','compatibility','authority'):
            v=deepcopy(self.record);rows={r['checkpoint']:r['execution'] for r in v['checkpoints']}
            if kind=='acceptance':v['user_accepted']=True
            elif kind=='missing':v['checkpoints'].pop()
            elif kind=='cells':rows['8.4d']['successful_history_cells']=42
            elif kind=='closure':v['full_GRC9V4_conformance']=True
            elif kind=='exclusion':v['original_large_target_roles_excluded']=['reset']
            elif kind=='compatibility':rows['9.3']['counts']['bounded_accepted']=24
            elif kind=='authority':rows['9.6']['authority'][0]['support_disposition']='supported'
            else:v['source_bindings']=[r for r in v['source_bindings'] if r['path']!=p.large.filename('step','reset',10)]
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.checked(value=p.b.seal(v))

    def test_source_drift_and_index_boundary(self):
        read=Path.read_bytes;target=ROOT/'src/pygrc/models/grc_9_v4_owner.py'
        with patch.object(Path,'read_bytes',lambda path:read(path)+b'# drift\n' if path==target else read(path)):
            with self.assertRaises(ValueError):cpc.cpc_status(ROOT)
        for name in ('../secret','src/../secret','/etc/passwd'):
            with self.subTest(name=name),self.assertRaises(KeyError):cpc.cpc_source(ROOT,name)
        raw,ref=cpc.cpc_source(ROOT,p.PATH);self.assertEqual(p.b.sha(raw),ref['sha256'])

    def test_fresh_checkout_restores_only_verified_cpc_oracles(self):
        from scripts import evidence_storage as storage
        rows=[r for r in storage.entries(ROOT) if r['path'].startswith(cpc.BASE+'P9-8.4g-CPC')]
        self.assertEqual({r['path'] for r in rows},{p.large.g.RESULTS,p.large.companion.RESULTS})
        with TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ('scripts/evidence_storage.py',*(r['storage_path'] for r in rows)):
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
            manifest=json.loads((ROOT/storage.MANIFEST).read_bytes());manifest['files']=rows
            (root/storage.MANIFEST).write_text(json.dumps(manifest));cpc.restore_inputs(root)
            for row in rows:self.assertEqual((root/row['path']).read_bytes(),(ROOT/row['path']).read_bytes())
            (root/rows[0]['path']).write_bytes(b'local drift')
            with self.assertRaises(ValueError):cpc.restore_inputs(root)
            self.assertEqual((root/rows[0]['path']).read_bytes(),b'local drift')

    def test_http_and_real_notebook_cell(self):
        spec=importlib.util.spec_from_file_location('cpc_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        def get(path):
            h=server.Handler.__new__(server.Handler);h.path,h.wfile=path,BytesIO();codes=[]
            h.send_response=codes.append;h.send_header=lambda *args:None;h.end_headers=lambda:None
            h.do_GET();return codes[-1],h.wfile.getvalue()
        code,raw=get('/api/cpc');self.assertEqual(code,200);self.assertEqual(json.loads(raw),self.status)
        code,raw=get('/api/cpc/source?path='+p.PATH)
        self.assertEqual(code,200);self.assertEqual(json.loads(raw),self.record)
        for path in ('/api/cpc?family=C_OS','/api/cpc?unused=',
                '/api/cpc/source?path=../secret','/api/cpc/source?path=x&path=y',
                '/api/cpc/source?path='+p.PATH+'&unused=',
                '/api/cpc/source?path='+p.PATH+'&path='):
            self.assertEqual(get(path)[0],404)
        code,raw=get('/cpc.js');self.assertEqual(code,200);self.assertEqual(raw,(TOOL/'phase9-web/cpc.js').read_bytes())
        with patch.object(server,'cpc_status',side_effect=ValueError('source drift')):
            code,raw=get('/api/cpc');self.assertEqual(code,503);self.assertEqual(set(json.loads(raw)),{'error'})
        book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(c for c in book['cells'] if c.get('id')=='query-cpc')
        code=compile(''.join(cell['source']),'cpc-notebook-cell','exec');namespace=dict(repo_root=ROOT)
        exec(code,namespace);self.assertEqual(namespace['phase9_cpc'],self.status)
        with patch.object(cpc,'cpc_status',side_effect=ValueError('drift')):
            with self.assertRaises(ValueError):exec(code,namespace)
            self.assertIsNone(namespace['phase9_cpc'])

    def test_browser_table_scope_and_failure_clearing(self):
        script="""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const value=JSON.parse(readFileSync(0,'utf8'));
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let listener,ok=true;
function element(tag){return {tag,children:[],append(e){this.children.push(e)},insertCell(){const e=element('td');this.append(e);return e},insertRow(){const e=element('tr');this.append(e);return e},createTHead(){const e=element('thead');this.append(e);return e},createTBody(){const e=element('tbody');this.append(e);return e}};}
globalThis.document={getElementById(id){return id==='cpc-refresh'?{addEventListener(_,fn){listener=fn}}:id==='cpc-status'?status:output},createElement:element};
globalThis.fetch=async()=>({ok,json:async()=>value});
const {cpcRows}=await import('./cpc.js');
assert.equal(cpcRows(value).length,16);
assert.throws(()=>cpcRows({...value,user_accepted:true}));
for (const field of ['checkpoint','state']) { const bad=structuredClone(value);bad.checkpoints[0][field]='invented';assert.throws(()=>cpcRows(bad)); }
await listener();assert.equal(output.children[0].tag,'table');assert.match(status.textContent,/review/);
ok=false;await listener();assert.equal(output.children.length,0);assert.match(status.textContent,/failed/);
const html=readFileSync('index.html','utf8');assert.match(html,/id="cpc-refresh"/);assert.match(html,/C_PC/);
"""
        result=subprocess.run([str(managed_node()),'--input-type=module','-e',script],
            input=json.dumps(self.status),text=True,capture_output=True,cwd=TOOL/'phase9-web',
            timeout=30,env=tool_environment())
        self.assertEqual(result.returncode,0,result.stderr)

    def test_accepted_predecessor_stays_accepted(self):
        from grcv4_explorer.aos import aos_status
        old=aos_status(ROOT)
        self.assertTrue(old['user_accepted']);self.assertFalse(self.status['user_accepted'])
        self.assertEqual(_profile_next_gate(dict(aos_work=old,cpc_work=self.status)),self.status['next_work'])
        self.assertTrue(all(row['state']=='bounded_accepted' for row in old['checkpoints']))
        import p9_aos_historical as historical
        name='tests/models/test_grc_9_v4_crossing.py'
        original=p.historical.original(ROOT,name)
        ref=historical.reference(ROOT,name)
        self.assertEqual(ref,dict(path=name,sha256=p.b.sha(original)))
        raw,metadata=historical.read_source(ROOT,ref)
        self.assertEqual(raw,original)
        self.assertEqual(metadata['revision'],p.historical.REVISION)
        read=Path.read_bytes;target=ROOT/name
        with patch.object(Path,'read_bytes',lambda path:read(path)+b'# drift\n' if path==target else read(path)):
            with self.assertRaises(ValueError):historical.reference(ROOT,name)
            with self.assertRaises(ValueError):historical.read_source(ROOT,ref)


class CPCTransportConstructionTests(unittest.TestCase):
    def test_prepared_transport_crosses_spawn_boundary_and_runs_native_event(self):
        n=p.large;c=p.large_covariance
        with p.wire_reuse(),n.compute_worker():
            manifest=n.g.storage.read(n.r.INPUTS)
            seed=n.r.state(manifest['expected_source']);case=manifest['cases'][0]
            (execution,predecessor,stats),seconds=n.process_budget.capped(c.child,
                ('combined','event',(seed.to_payload(),case,'private-small-parity')),60)
            self.assertEqual(predecessor,'private-small-parity')
            self.assertTrue(execution['event']['replay_identical'])
            self.assertEqual(execution['state'],n.check_event(seed,case,execution['event']).to_payload())
            self.assertGreater(stats['requests'],0);self.assertEqual(stats['retained_bytes'],0)

    def test_direct_transformed_construction_matches_full_reconstruction(self):
        n=p.large;c=p.large_covariance
        with p.wire_reuse(),n.compute_worker():
            manifest=n.g.storage.read(n.r.INPUTS)
            seed=n.r.state(manifest['expected_source']);case=manifest['cases'][0]
            target=n.independent_target(manifest,case)
            with patch.object(c.maps,'base',return_value=(seed.to_payload(),{})):
                for kind in c.KINDS:
                    declaration=c.maps.declaration(kind)
                    for inputs in (seed.inputs,target):
                        raw=inputs.to_payload();eid=case['oracle']['event_id']
                        graph=c.maps.graph_image(raw['reference']['graph'],declaration,eid,eid,
                            source=inputs is seed.inputs)
                        with self.subTest(kind=kind,target=inputs is target):
                            direct=c.input_image(raw,graph,declaration,eid,eid)
                            reconstructed=c.input_image(raw,graph,declaration,eid,eid,
                                before=p.b.GeometryStageInputs.from_payload(raw))
                            self.assertEqual(direct,reconstructed)
                            self.assertEqual(direct.to_payload(),reconstructed.to_payload())


if __name__=='__main__':unittest.main()
