"""C_CI_PC pending-research API/browser/notebook and predecessor pressure."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
import subprocess
import unittest
from unittest.mock import patch
import check_spark_completion_ci_pc_research as check
from grcv4_explorer import spark_cipc_research as research
from grcv4_explorer import spark_pc as prior
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node, tool_environment

ROOT,SIDE=check.ROOT,check.SIDE
TOOL=SIDE/'tool'


class ResearchSurfaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.view=research.spark_cipc_research_status(ROOT,SIDE)

    def test_bound_report_and_accepted_predecessor_are_distinct(self):
        self.assertEqual(check.check()['retained_states'],self.view['report']['verification']['retained_states'])
        view=prior.spark_pc_authority(ROOT,SIDE)
        self.assertEqual(view['scope']['scientific_families'],['C_OS','C_CI','C_PC'])
        self.assertEqual(next(r for r in view['family_dispositions'] if r['family']=='C_CI_PC')['status'],
                         'not_yet_investigated')  # immutable accepted checkpoint
        self.assertEqual(self.view['report']['status'],'demonstrated_bounded_pending_review')
        self.assertEqual(self.view['report']['decisions']['reset']['local_gain'],0)
        self.assertFalse(self.view['report']['accepted_authority'])

    def test_rehashed_widening_and_bound_source_drift_reject(self):
        original=research.load_json_object
        for field,value in [('accepted_authority',True),('full_dimension',14),('status','accepted_bounded_scientific'),
                            ('native_support_added',['C_CI_PC']),('G4_accepted',True),('review_limits',[])]:
            def altered(path):
                v=deepcopy(original(path))
                if path==ROOT/research.REPORT:
                    v[field]=value;v['record_digest']=record_digest(v,'record_digest')
                return v
            with self.subTest(field=field),patch.object(research,'load_json_object',altered):
                with self.assertRaises(SourceAdmissionError):research.spark_cipc_research_status(ROOT,SIDE)
        bound=research._bound_file
        def drift(root,path,digest):
            if path.endswith('CCIPC-current.json.xz'):raise SourceAdmissionError('changed retained trajectory')
            return bound(root,path,digest)
        with patch.object(research,'_bound_file',drift),self.assertRaises(SourceAdmissionError):
            research.spark_cipc_research_status(ROOT,SIDE)
        with self.assertRaises(KeyError):research.spark_cipc_research_source(ROOT,SIDE,'../outside')

    def test_metadata_successor_rejects_rehash_and_wrong_preimage(self):
        from grcv4_explorer import spark_cipc_metadata as epochs
        original=epochs.load_json_object
        def altered(path):
            value=deepcopy(original(path));value['sources'][0]['after_sha256']='0'*64
            value['record_digest']=record_digest(value,'record_digest');return value
        with patch.object(epochs,'load_json_object',altered),self.assertRaises(SourceAdmissionError):
            epochs.checked_successor(ROOT)
        with patch.object(epochs.subprocess,'check_output',return_value=b'wrong'),self.assertRaises(SourceAdmissionError):
            epochs.checked_successor(ROOT)
        self.assertEqual(prior.spark_pc_authority(ROOT,SIDE)['projection_digest'],
                         '3f7489e3d8fd1f97b3bc7f6a6053580bd2ade60c5bfcbf7b0b89924684363796')

    def test_real_http_and_indexed_source(self):
        spec=importlib.util.spec_from_file_location('pc_research_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        h=server.Handler.__new__(server.Handler);codes=[]
        h.send_response=codes.append;h.send_header=lambda *a:None;h.end_headers=lambda:None
        h.path='/api/spark-completion/applicability/ci-pc/research';h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],200);self.assertEqual(json.loads(h.wfile.getvalue()),self.view)
        with patch.object(server,'spark_cipc_research_status',side_effect=SourceAdmissionError('held')):
            h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],503);self.assertEqual(set(json.loads(h.wfile.getvalue())),{'error'})
        h.path+='?family=C_CI_PC';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],404)
        h.path='/api/spark-completion/applicability/ci-pc/research/source?path='+research.REPORT
        h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(ROOT/research.REPORT).read_bytes())
        h.path='/spark-cipc-research.js';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(TOOL/'phase9-web/spark-cipc-research.js').read_bytes())

    def test_real_notebook_cell_clears_failed_refresh(self):
        book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(c for c in book['cells'] if c.get('id')=='spark-completion-ci-pc-research')
        code=compile(''.join(cell['source']),'spark-cipc-research-notebook','exec');ns={'repo_root':ROOT}
        exec(code,ns);self.assertEqual(ns['phase9_spark_cipc_research'],self.view)
        with patch.object(research,'spark_cipc_research_status',side_effect=SourceAdmissionError('held')):
            with self.assertRaises(SourceAdmissionError):exec(code,ns)
        self.assertIsNone(ns['phase9_spark_cipc_research'])

    def test_managed_browser_pending_scope_and_failed_refresh(self):
        js=r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalBasin} from './basin.js';
import {checkedSparkCIPCResearch,sparkCIPCResearchLoader} from './spark-cipc-research.js';
const v=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedSparkCIPCResearch(v),v);
for(const edit of [x=>x.report.accepted_authority=true,x=>x.report.full_dimension=14,
 x=>x.report.native_support_added.push('C_CI_PC'),x=>x.report.review_limits=[],
 x=>x.accepted_scientific_families.push('C_CI_PC'),x=>x.source_refs.pop()]) {
 const b=structuredClone(v);edit(b);delete b.report.record_digest;
 b.report.record_digest=createHash('sha256').update(canonicalBasin(b.report)).digest('hex');
 delete b.projection_digest;b.projection_digest=createHash('sha256').update(canonicalBasin(b)).digest('hex');
 await assert.rejects(checkedSparkCIPCResearch(b));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=sparkCIPCResearchLoader(output,status,async()=>({ok,json:async()=>v}),tag=>({tag}));
await load();assert.ok(output.children.length>20);assert.match(status.textContent,/acceptance remain pending/);
assert.ok(output.children.some(e=>e.textContent.includes('46 carrier directions')));
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
assert.match(readFileSync('index.html','utf8'),/id="spark-cipc-research-refresh"/);
console.log('CCIPC_RESEARCH_BROWSER_PASS');
'''
        result=subprocess.run([str(managed_node()),'--input-type=module','-e',js],
            cwd=TOOL/'phase9-web',input=json.dumps(self.view),text=True,capture_output=True,
            timeout=30,env=tool_environment())
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'CCIPC_RESEARCH_BROWSER_PASS')


if __name__=='__main__':unittest.main()
