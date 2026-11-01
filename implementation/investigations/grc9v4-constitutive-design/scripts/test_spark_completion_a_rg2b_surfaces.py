"""A_RG2b research scope, finite succession, HTTP, browser and notebook checks."""
from copy import deepcopy
from io import BytesIO
import importlib.util,json,subprocess,unittest,hashlib
from unittest.mock import patch
import check_spark_completion_a_rg2b_research as check
from grcv4_explorer import spark_arg2b_research as research,spark_arg2b_metadata as epochs
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node,tool_environment
ROOT,SIDE=check.ROOT,check.SIDE;TOOL=SIDE/'tool'


class ARG2bResearchSurfaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.view=research.spark_arg2b_research_status(ROOT,SIDE)

    def test_bound_full_state_direct_scope(self):
        r=self.view['report'];self.assertEqual(check.check()['retained_states'],604)
        self.assertEqual(r['full_dimension'],30);self.assertEqual(r['full_state'],['C','W_A'])
        self.assertEqual(r['last_executed_step'],302);self.assertFalse(r['future_trajectory_required'])
        self.assertEqual(r['supporting_trajectory_steps_after_completion'],0)
        self.assertEqual(r['proof']['trajectory_inputs_to_domain_checker'],0)
        self.assertTrue(r['proof']['physical']['full_writer_included'])
        self.assertFalse(r['proof']['section_C1_claimed']);self.assertFalse(r['accepted_authority'])
        self.assertEqual(r['decisions']['current']['local_gain'],1)
        self.assertEqual(r['decisions']['reset']['local_gain'],0)

    def test_rehashed_scope_changes_and_source_drift_reject(self):
        original=research.load_json_object
        defects=[('accepted_authority',True),('full_dimension',14),('ordinary_duration','32'),
            ('entry',250),('completion',301),('last_executed_step',2000),
            ('supporting_trajectory_steps_after_completion',1697),('future_trajectory_required',True),
            ('native_completion',True),('G4_accepted',True),('retained_states',600)]
        for key,value in defects:
            def altered(path):
                v=deepcopy(original(path))
                if path==ROOT/research.REPORT:v[key]=value;v['record_digest']=record_digest(v,'record_digest')
                return v
            with self.subTest(key=key),patch.object(research,'load_json_object',altered),self.assertRaises(SourceAdmissionError):
                research.spark_arg2b_research_status(ROOT,SIDE)
        bound=research._bound_file
        def drift(root,path,digest):
            if path.endswith('ARG2b-current.json.xz'):raise SourceAdmissionError('changed selected prefix')
            return bound(root,path,digest)
        with patch.object(research,'_bound_file',drift),self.assertRaises(SourceAdmissionError):
            research.spark_arg2b_research_status(ROOT,SIDE)

    def test_metadata_preimages_and_exact_roster(self):
        self.assertEqual(len(epochs.checked_epoch(ROOT)['sources']),9)
        original=epochs.load_json_object
        def altered(path):
            v=deepcopy(original(path));v['sources'].pop();v['record_digest']=record_digest(v,'record_digest');return v
        with patch.object(epochs,'load_json_object',altered),self.assertRaises(SourceAdmissionError):epochs.checked_epoch(ROOT)
        with patch.object(epochs.subprocess,'check_output',return_value=b'wrong'),self.assertRaises(SourceAdmissionError):epochs.checked_epoch(ROOT)
        with self.assertRaises(SourceAdmissionError):epochs.bound_metadata_files(ROOT,{'specs/grc-v4-spec.md':'0'*64})
        before=subprocess.check_output(['git','show',epochs.BASELINE+':'+epochs.HISTORICAL_HELPER],cwd=ROOT)
        self.assertEqual(epochs.reviewed_source_bytes(ROOT,epochs.HISTORICAL_HELPER,hashlib.sha256(before).hexdigest()),before)
        self.assertNotEqual(before,(ROOT/epochs.HISTORICAL_HELPER).read_bytes())

    def test_preserved_accepted_crg2b_and_older_research(self):
        from grcv4_explorer.spark_crg2b import spark_crg2b_authority
        from grcv4_explorer.spark_crg2b_research import spark_crg2b_research_status
        from grcv4_explorer.spark_aos_earlier import spark_aos_earlier_status
        accepted=spark_crg2b_authority(ROOT,SIDE)
        self.assertEqual(accepted['projection_digest'],'7100f5eea0a3d64f3aa753a4fdb03a54ff34ad534f0159e6d3039ca2ae03873f')
        self.assertEqual(accepted['scope']['scientific_families'],research.FAMILIES)
        self.assertEqual(spark_crg2b_research_status(ROOT,SIDE)['projection_digest'],'26581fd460e458eefa5a8742e2840bb6d09e54fc3b6e24dbd1c41159b9f276cc')
        self.assertEqual(spark_aos_earlier_status(ROOT,SIDE)['projection_digest'],'7b2ebfe5b2f8bcad90c0fc3d69aa5d4e86dad3c5ec165301938f4d617ccf116a')

    def test_http_download_and_failure(self):
        spec=importlib.util.spec_from_file_location('arg2b_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        h=server.Handler.__new__(server.Handler);codes=[];headers={};h.command='GET'
        h.send_response=lambda code,message=None:codes.append(code);h.send_header=lambda k,v:headers.__setitem__(k,v);h.end_headers=lambda:None
        h.path='/api/spark-completion/applicability/a-rg2b/research';h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],200);self.assertEqual(json.loads(h.wfile.getvalue()),self.view)
        with patch.object(server,'spark_arg2b_research_status',side_effect=SourceAdmissionError('held')):
            h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],503);self.assertEqual(set(json.loads(h.wfile.getvalue())),{'error'})
        h.path+='?family=A_RG2b';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],404)
        h.path='/api/spark-completion/applicability/a-rg2b/research/source?path='+research.BASE+'ARG2b-current.json.xz'
        h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(ROOT/(research.BASE+'ARG2b-current.json.xz')).read_bytes())
        with self.assertRaises(KeyError):research.spark_arg2b_research_source(ROOT,SIDE,'../outside')
        h.path='/spark-arg2b-research.js';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(TOOL/'phase9-web/spark-arg2b-research.js').read_bytes())
        self.assertEqual(headers['Content-Type'],'text/javascript')

    def test_notebook_clears_stale_result(self):
        book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(c for c in book['cells'] if c.get('id')=='spark-completion-a-rg2b-research')
        code=compile(''.join(cell['source']),'arg2b-notebook','exec');ns={'repo_root':ROOT}
        exec(code,ns);self.assertEqual(ns['phase9_spark_arg2b_research'],self.view)
        with patch.object(research,'spark_arg2b_research_status',side_effect=SourceAdmissionError('held')):
            with self.assertRaises(SourceAdmissionError):exec(code,ns)
        self.assertIsNone(ns['phase9_spark_arg2b_research'])

    def test_browser_hash_scope_failed_and_stale_refresh(self):
        js=r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalBasin} from './basin.js';
import {checkedSparkARG2bResearch,sparkARG2bResearchLoader} from './spark-arg2b-research.js';
const v=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedSparkARG2bResearch(v),v);
for(const edit of [x=>x.report.accepted_authority=true,x=>x.report.proof.section_C1_claimed=true,
 x=>x.report.proof.physical.full_writer_included=false,x=>x.report.full_dimension=14,
 x=>x.report.last_executed_step=2089,x=>x.report.supporting_trajectory_steps_after_completion=1787,
 x=>x.report.ordinary_duration='32',x=>x.report.decisions.reset.local_gain=1,x=>x.report.review_limits=[]]) {
 const b=structuredClone(v);edit(b);delete b.report.record_digest;
 b.report.record_digest=createHash('sha256').update(canonicalBasin(b.report)).digest('hex');
 b.report_record_digest=b.report.record_digest;delete b.projection_digest;
 b.projection_digest=createHash('sha256').update(canonicalBasin(b)).digest('hex');
 await assert.rejects(checkedSparkARG2bResearch(b));
}
const unbound=structuredClone(v);unbound.report.proof.radius='1';await assert.rejects(checkedSparkARG2bResearch(unbound));
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=sparkARG2bResearchLoader(output,status,async()=>({ok,json:async()=>v}),tag=>({tag}));
await load();assert.ok(output.children.length>10);assert.match(status.textContent,/nine scientific families/);
assert.ok(output.children.some(e=>e.textContent.includes('Last executed step: 302. Subsequent supporting steps: 0.')));
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
let resolve;
const race=sparkARG2bResearchLoader(output,status,()=>new Promise(r=>{resolve=r}),tag=>({tag}));
const first=race();const old=resolve;const second=race();resolve({ok:false});await second;
old({ok:true,json:async()=>v});await first;assert.equal(output.children.length,0);
assert.match(readFileSync('index.html','utf8'),/id="spark-arg2b-research-refresh"/);
console.log('ARG2b_BROWSER_PASS');
'''
        r=subprocess.run([str(managed_node()),'--input-type=module','-e',js],cwd=TOOL/'phase9-web',input=json.dumps(self.view),
            text=True,capture_output=True,timeout=30,env=tool_environment())
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(r.stdout.strip(),'ARG2b_BROWSER_PASS')


if __name__=='__main__':unittest.main(verbosity=2)
