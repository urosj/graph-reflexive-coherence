"""A_CI pending research, exact predecessors, HTTP/browser/notebook pressure."""
from copy import deepcopy
from io import BytesIO
import importlib.util,json,subprocess,unittest
from unittest.mock import patch
import check_spark_completion_a_ci_research as check
from grcv4_explorer import spark_aci_research as research,spark_aci_metadata as epochs
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node,tool_environment
ROOT,SIDE=check.ROOT,check.SIDE;TOOL=SIDE/'tool'


class ACIResearchSurfaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.view=research.spark_aci_research_status(ROOT,SIDE)

    def test_bound_proof_decisions_and_retained_checks(self):
        self.assertEqual(check.check()['retained_states'],751);r=self.view['report']
        self.assertEqual([r['decisions'][role]['target_completion_step'] for role in ('current','reset')],[377,374])
        self.assertTrue(r['proof']['implicit_geometry_derivative']);self.assertFalse(r['proof']['OS_derivative_reused'])
        self.assertFalse(r['accepted_authority']);self.assertEqual(r['decisions']['reset']['local_gain'],0)

    def test_rehashed_scope_source_and_root_changes_reject(self):
        original=research.load_json_object
        for defect in ('acceptance','missing_W','root','OS','native','gain','review'):
            def altered(path):
                v=deepcopy(original(path))
                if path==ROOT/research.REPORT:
                    if defect=='acceptance':v['accepted_authority']=True
                    if defect=='missing_W':v['conductance_dimension']=15
                    if defect=='root':v['proof']['implicit_geometry_derivative']=False
                    if defect=='OS':v['proof']['OS_trajectory_reused']=True
                    if defect=='native':v['native_completion']=True
                    if defect=='gain':v['decisions']['reset']['local_gain']=1
                    if defect=='review':v['review_limits']=[]
                    v['record_digest']=record_digest(v,'record_digest')
                return v
            with self.subTest(defect=defect),patch.object(research,'load_json_object',altered),self.assertRaises(SourceAdmissionError):
                research.spark_aci_research_status(ROOT,SIDE)
        bound=research._bound_file
        def drift(root,path,digest):
            if path.endswith('ACI-current.json.xz'):raise SourceAdmissionError('changed trajectory')
            return bound(root,path,digest)
        with patch.object(research,'_bound_file',drift),self.assertRaises(SourceAdmissionError):research.spark_aci_research_status(ROOT,SIDE)

    def test_metadata_preimage_and_path_controls(self):
        self.assertEqual(len(epochs.checked_epoch(ROOT)['sources']),10)
        original=epochs.load_json_object
        def altered(path):
            v=deepcopy(original(path));v['sources'].pop();v['record_digest']=record_digest(v,'record_digest');return v
        with patch.object(epochs,'load_json_object',altered),self.assertRaises(SourceAdmissionError):epochs.checked_epoch(ROOT)
        with patch.object(epochs.subprocess,'check_output',return_value=b'wrong'),self.assertRaises(SourceAdmissionError):epochs.checked_epoch(ROOT)
        with self.assertRaises(SourceAdmissionError):epochs.bound_metadata_files(ROOT,{'specs/grc-v4-spec.md':'0'*64})

    def test_preserved_accepted_and_both_aos_research_views(self):
        from grcv4_explorer.spark_aos import spark_aos_authority
        from grcv4_explorer.spark_aos_research import spark_aos_research_status
        from grcv4_explorer.spark_aos_earlier import spark_aos_earlier_status,spark_aos_earlier_source
        accepted=spark_aos_authority(ROOT,SIDE)
        self.assertEqual(accepted['projection_digest'],'5006a5e76811aed03c41c32088cb5775068f6247dfaf3a4640c10e3d93704afb')
        self.assertEqual(accepted['scope']['scientific_families'],['C_OS','C_CI','C_PC','C_CI_PC','A_OS'])
        self.assertEqual(spark_aos_research_status(ROOT,SIDE)['projection_digest'],'a96cfbe550a3dd59f8d8797b0cdf068914274403561f37aae68fab6354ae8f0f')
        self.assertEqual(spark_aos_earlier_status(ROOT,SIDE)['projection_digest'],'7b2ebfe5b2f8bcad90c0fc3d69aa5d4e86dad3c5ec165301938f4d617ccf116a')
        data,ref=spark_aos_earlier_source(ROOT,SIDE,epochs.HISTORICAL_HELPER)
        self.assertEqual(data,subprocess.check_output(['git','show',epochs.BASELINE+':'+epochs.HISTORICAL_HELPER],cwd=ROOT))
        self.assertNotEqual(data,(ROOT/epochs.HISTORICAL_HELPER).read_bytes())
        with self.assertRaises(SourceAdmissionError):epochs.reviewed_source_bytes(ROOT,epochs.HISTORICAL_HELPER,'0'*64)

    def test_http_indexed_download_and_failed_refresh(self):
        spec=importlib.util.spec_from_file_location('aci_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        h=server.Handler.__new__(server.Handler);codes=[];h.command='GET'
        h.send_response=lambda code,message=None:codes.append(code);h.send_header=lambda *a:None;h.end_headers=lambda:None
        h.path='/api/spark-completion/applicability/a-ci/research';h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],200);self.assertEqual(json.loads(h.wfile.getvalue()),self.view)
        with patch.object(server,'spark_aci_research_status',side_effect=SourceAdmissionError('held')):
            h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],503);self.assertEqual(set(json.loads(h.wfile.getvalue())),{'error'})
        h.path+='?family=A_CI';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],404)
        h.path='/api/spark-completion/applicability/a-ci/research/source?path='+research.BASE+'ACI-current.json.xz'
        h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(ROOT/(research.BASE+'ACI-current.json.xz')).read_bytes())
        with self.assertRaises(KeyError):research.spark_aci_research_source(ROOT,SIDE,'../outside')
        for name in ('spark-aci-research.js','spark-aos-earlier.js'):
            h.path='/'+name;h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
            self.assertEqual(h.wfile.getvalue(),(TOOL/'phase9-web'/name).read_bytes())
        h.path='/not-a-panel.js';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],404)

    def test_notebook_clears_stale_result(self):
        book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(c for c in book['cells'] if c.get('id')=='spark-completion-a-ci-research')
        code=compile(''.join(cell['source']),'aci-notebook','exec');ns={'repo_root':ROOT}
        exec(code,ns);self.assertEqual(ns['phase9_spark_aci_research'],self.view)
        with patch.object(research,'spark_aci_research_status',side_effect=SourceAdmissionError('held')):
            with self.assertRaises(SourceAdmissionError):exec(code,ns)
        self.assertIsNone(ns['phase9_spark_aci_research'])

    def test_browser_scope_failed_and_stale_refresh(self):
        js=r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalBasin} from './basin.js';
import {checkedSparkACIResearch,sparkACIResearchLoader} from './spark-aci-research.js';
const v=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedSparkACIResearch(v),v);
for(const edit of [x=>x.report.accepted_authority=true,x=>x.report.proof.implicit_geometry_derivative=false,
 x=>x.report.conductance_dimension=15,x=>x.report.decisions.reset.local_gain=1,x=>x.report.review_limits=[]]) {
 const b=structuredClone(v);edit(b);delete b.report.record_digest;
 b.report.record_digest=createHash('sha256').update(canonicalBasin(b.report)).digest('hex');
 b.report_record_digest=b.report.record_digest;delete b.projection_digest;
 b.projection_digest=createHash('sha256').update(canonicalBasin(b)).digest('hex');
 await assert.rejects(checkedSparkACIResearch(b));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=sparkACIResearchLoader(output,status,async()=>({ok,json:async()=>v}),tag=>({tag}));
await load();assert.ok(output.children.length>20);assert.match(status.textContent,/five scientific families/);
assert.ok(output.children.some(e=>e.textContent.includes('entry 375; two-beat window ends at 377')));
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
let resolve;
const race=sparkACIResearchLoader(output,status,()=>new Promise(r=>{resolve=r}),tag=>({tag}));
const first=race();const old=resolve;const second=race();resolve({ok:false});await second;
old({ok:true,json:async()=>v});await first;assert.equal(output.children.length,0);
assert.match(readFileSync('index.html','utf8'),/id="spark-aci-research-refresh"/);
console.log('ACI_BROWSER_PASS');
'''
        r=subprocess.run([str(managed_node()),'--input-type=module','-e',js],cwd=TOOL/'phase9-web',input=json.dumps(self.view),text=True,capture_output=True,timeout=30,env=tool_environment())
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(r.stdout.strip(),'ACI_BROWSER_PASS')


if __name__=='__main__':unittest.main()
