"""C_RG2b pending research, exact predecessors, HTTP/browser/notebook pressure."""
from copy import deepcopy
from io import BytesIO
import importlib.util,json,subprocess,unittest
from unittest.mock import patch
import check_spark_completion_c_rg2b_research as check
from grcv4_explorer import spark_crg2b_research as research,spark_crg2b_metadata as epochs
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node,tool_environment
ROOT,SIDE=check.ROOT,check.SIDE;TOOL=SIDE/'tool'


class CRG2bResearchSurfaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.view=research.spark_crg2b_research_status(ROOT,SIDE)

    def test_bound_proof_decisions_and_retained_checks(self):
        r=self.view['report'];self.assertEqual(check.check()['retained_states'],r['verification']['retained_states'])
        self.assertEqual(r['verification']['retained_states'],784)
        self.assertEqual(check.check()['historical_summary_states'],4250)
        self.assertFalse(r['historical_baseline']['numerical_payloads_retained'])
        for role in ('current','reset'):
            self.assertFalse((ROOT/(research.BASE+'CRG2b-'+role+'.json.xz')).exists())
            self.assertNotIn(research.BASE+'CRG2b-'+role+'.json.xz',{ref['path'] for ref in self.view['source_refs']})
        for role in ('current','reset'):
            d=r['decisions'][role];self.assertEqual(d['target_completion_step'],d['first_certified_entry']+2)
            self.assertEqual(d['window_elapsed'],'16')
            self.assertEqual(r['elapsed_from_event'][role]['completion'],str(8*d['target_completion_step']))
        self.assertEqual(r['faster']['completion'],392);self.assertEqual(r['faster']['proof']['component_radius'],'1/32768')
        self.assertEqual(r['direct']['complete_fresh_trajectory_replays'],2);self.assertFalse(r['faster']['uniform_duration_32_certified'])
        self.assertEqual(r['selected_proof'],'direct_continuous_domain')
        self.assertEqual(r['direct']['last_executed_step'],392)
        self.assertEqual(r['direct']['supporting_trajectory_steps_after_completion'],0)
        self.assertFalse(r['direct']['future_trajectory_required'])
        self.assertEqual(r['direct']['proof']['trajectory_inputs_to_domain_checker'],0)
        self.assertEqual(r['faster']['status'],'historical_summary_only')
        for role in ('current','reset'):
            retired=research.BASE+'CRG2bFaster-'+role+'.json.xz'
            self.assertFalse((ROOT/retired).exists())
            self.assertNotIn(retired,{ref['path'] for ref in self.view['source_refs']})
        self.assertTrue(r['proof']['full_return_difference_bound']);self.assertEqual(r['full_dimension'],14)
        self.assertFalse(r['proof']['section_C1_claimed']);self.assertFalse(r['accepted_authority'])
        self.assertEqual(r['decisions']['reset']['local_gain'],0)

    def test_rehashed_scope_source_and_section_changes_reject(self):
        original=research.load_json_object
        for defect in ('acceptance','C1','completion','history','old_trajectory','native','gain','review','tail','direct_C1','direct_dimension'):
            def altered(path):
                v=deepcopy(original(path))
                if path==ROOT/research.REPORT:
                    if defect=='acceptance':v['accepted_authority']=True
                    if defect=='C1':v['proof']['section_C1_claimed']=True
                    if defect=='completion':v['proof']['completion_relative']=False
                    if defect=='history':v['proof']['geometry_history_transported']=True
                    if defect=='old_trajectory':v['proof']['earlier_family_trajectory_reused']=True
                    if defect=='native':v['native_completion']=True
                    if defect=='gain':v['decisions']['reset']['local_gain']=1
                    if defect=='review':v['review_limits']=[]
                    if defect=='tail':v['direct']['supporting_trajectory_steps_after_completion']=1697
                    if defect=='direct_C1':v['direct']['proof']['section_C1_claimed']=True
                    if defect=='direct_dimension':v['direct']['proof']['relative_dimension']=13
                    v['record_digest']=record_digest(v,'record_digest')
                return v
            with self.subTest(defect=defect),patch.object(research,'load_json_object',altered),self.assertRaises(SourceAdmissionError):
                research.spark_crg2b_research_status(ROOT,SIDE)
        bound=research._bound_file
        def drift(root,path,digest):
            if path.endswith('CRG2bDirect-current.json.xz'):raise SourceAdmissionError('changed trajectory')
            return bound(root,path,digest)
        with patch.object(research,'_bound_file',drift),self.assertRaises(SourceAdmissionError):research.spark_crg2b_research_status(ROOT,SIDE)

    def test_metadata_preimage_and_path_controls(self):
        self.assertEqual(len(epochs.checked_epoch(ROOT)['sources']),9)
        original=epochs.load_json_object
        def altered(path):
            v=deepcopy(original(path));v['sources'].pop();v['record_digest']=record_digest(v,'record_digest');return v
        with patch.object(epochs,'load_json_object',altered),self.assertRaises(SourceAdmissionError):epochs.checked_epoch(ROOT)
        with patch.object(epochs.subprocess,'check_output',return_value=b'wrong'),self.assertRaises(SourceAdmissionError):epochs.checked_epoch(ROOT)
        with self.assertRaises(SourceAdmissionError):epochs.bound_metadata_files(ROOT,{'specs/grc-v4-spec.md':'0'*64})

    def test_preserved_accepted_acipc_and_historical_views(self):
        from grcv4_explorer.spark_acipc import spark_acipc_authority
        from grcv4_explorer.spark_acipc_research import spark_acipc_research_status,spark_acipc_research_source
        from grcv4_explorer.spark_aos_earlier import spark_aos_earlier_status
        from grcv4_explorer import spark_acipc_sc3_metadata as accepted_epochs
        accepted=spark_acipc_authority(ROOT,SIDE)
        self.assertEqual(accepted['projection_digest'],'b8e182fce5c187023ba4d91921633e4d12e716c9b1408c83bad38fbacbec79f0')
        self.assertEqual(accepted['scope']['scientific_families'],['C_OS','C_CI','C_PC','C_CI_PC','A_OS','A_CI','A_PC','A_CI_PC'])
        self.assertEqual(spark_acipc_research_status(ROOT,SIDE)['projection_digest'],'b935ff772e9974a6f2b9cb16b15f7d10b58a15cfdde8d973df46b7c611f47ce0')
        self.assertEqual(spark_aos_earlier_status(ROOT,SIDE)['projection_digest'],'7b2ebfe5b2f8bcad90c0fc3d69aa5d4e86dad3c5ec165301938f4d617ccf116a')
        data,ref=spark_acipc_research_source(ROOT,SIDE,accepted_epochs.HISTORICAL_HELPER)
        self.assertEqual(data,subprocess.check_output(['git','show',accepted_epochs.REVIEWED_COMMIT+':'+ref['path']],cwd=ROOT))
        import hashlib
        previous=subprocess.check_output(['git','show',epochs.BASELINE+':'+epochs.HISTORICAL_HELPER],cwd=ROOT)
        self.assertEqual(epochs.reviewed_source_bytes(ROOT,epochs.HISTORICAL_HELPER,hashlib.sha256(previous).hexdigest()),previous)
        self.assertNotEqual(previous,(ROOT/epochs.HISTORICAL_HELPER).read_bytes())
        with self.assertRaises(SourceAdmissionError):epochs.reviewed_source_bytes(ROOT,epochs.HISTORICAL_HELPER,'0'*64)

    def test_http_indexed_download_and_failed_refresh(self):
        spec=importlib.util.spec_from_file_location('crg2b_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        h=server.Handler.__new__(server.Handler);codes=[];h.command='GET'
        headers={}
        h.send_response=lambda code,message=None:codes.append(code);h.send_header=lambda k,v:headers.__setitem__(k,v);h.end_headers=lambda:None
        h.path='/api/spark-completion/applicability/c-rg2b/research';h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],200);self.assertEqual(json.loads(h.wfile.getvalue()),self.view)
        with patch.object(server,'spark_crg2b_research_status',side_effect=SourceAdmissionError('held')):
            h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],503);self.assertEqual(set(json.loads(h.wfile.getvalue())),{'error'})
        h.path+='?family=C_RG2b';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],404)
        h.path='/api/spark-completion/applicability/c-rg2b/research/source?path='+research.BASE+'CRG2bDirect-current.json.xz'
        h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(ROOT/(research.BASE+'CRG2bDirect-current.json.xz')).read_bytes())
        with self.assertRaises(KeyError):research.spark_crg2b_research_source(ROOT,SIDE,'../outside')
        with self.assertRaises(KeyError):research.spark_crg2b_research_source(ROOT,SIDE,research.BASE+'CRG2b-current.json.xz')
        with self.assertRaises(KeyError):research.spark_crg2b_research_source(ROOT,SIDE,research.BASE+'CRG2bFaster-current.json.xz')
        for name in ('spark-crg2b-research.js','spark-acipc.js'):
            h.path='/'+name;h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
            self.assertEqual(h.wfile.getvalue(),(TOOL/'phase9-web'/name).read_bytes())
            self.assertEqual(headers['Content-Type'],'text/javascript')
        h.path='/not-a-panel.js';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],404)

    def test_notebook_clears_stale_result(self):
        book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(c for c in book['cells'] if c.get('id')=='spark-completion-c-rg2b-research')
        code=compile(''.join(cell['source']),'crg2b-notebook','exec');ns={'repo_root':ROOT}
        exec(code,ns);self.assertEqual(ns['phase9_spark_crg2b_research'],self.view)
        with patch.object(research,'spark_crg2b_research_status',side_effect=SourceAdmissionError('held')):
            with self.assertRaises(SourceAdmissionError):exec(code,ns)
        self.assertIsNone(ns['phase9_spark_crg2b_research'])

    def test_browser_scope_failed_and_stale_refresh(self):
        js=r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalBasin} from './basin.js';
import {checkedSparkCRG2bResearch,sparkCRG2bResearchLoader} from './spark-crg2b-research.js';
const v=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedSparkCRG2bResearch(v),v);
for(const edit of [x=>x.report.accepted_authority=true,x=>x.report.proof.section_C1_claimed=true,
 x=>x.report.proof.full_return_difference_bound=false,x=>x.report.proof.completion_relative=false,
 x=>x.report.historical_baseline.numerical_payloads_retained=true,x=>x.report.faster.completion=391,x=>x.report.faster.proof.original_SC1_contract_unchanged=false,
 x=>x.report.faster.uniform_duration_32_certified=true,x=>x.report.faster.decisions.reset.local_gain=1,
 x=>x.report.direct.last_executed_step=2089,x=>x.report.direct.supporting_trajectory_steps_after_completion=1697,
 x=>x.report.direct.proof.trajectory_inputs_to_domain_checker=1,x=>x.report.direct.proof.common_contraction.both_H_consumers=false,
 x=>x.report.ordinary_duration='32',x=>x.report.full_dimension=13,x=>x.report.proof.geometry_history_transported=true,x=>x.report.decisions.reset.local_gain=1,x=>x.report.review_limits=[]]) {
 const b=structuredClone(v);edit(b);delete b.report.record_digest;
 b.report.record_digest=createHash('sha256').update(canonicalBasin(b.report)).digest('hex');
 b.report_record_digest=b.report.record_digest;delete b.projection_digest;
 b.projection_digest=createHash('sha256').update(canonicalBasin(b)).digest('hex');
 await assert.rejects(checkedSparkCRG2bResearch(b));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=sparkCRG2bResearchLoader(output,status,async()=>({ok,json:async()=>v}),tag=>({tag}));
await load();assert.ok(output.children.length>20);assert.match(status.textContent,/eight scientific families/);
assert.ok(output.children.some(e=>e.textContent.includes(`entry ${v.report.decisions.current.first_certified_entry}; two-beat window ends at ${v.report.decisions.current.target_completion_step}`)));
assert.ok(output.children.some(e=>e.textContent.includes(`completion ${v.report.elapsed_from_event.current.completion}`)));
assert.ok(output.children.some(e=>e.textContent.includes('selected entry 390; completion 392; last executed step 392; subsequent supporting steps 0')));
assert.ok(output.children.some(e=>e.textContent.includes('their full trajectory files were removed')));
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
let resolve;
const race=sparkCRG2bResearchLoader(output,status,()=>new Promise(r=>{resolve=r}),tag=>({tag}));
const first=race();const old=resolve;const second=race();resolve({ok:false});await second;
old({ok:true,json:async()=>v});await first;assert.equal(output.children.length,0);
assert.match(readFileSync('index.html','utf8'),/id="spark-crg2b-research-refresh"/);
console.log('CRG2b_BROWSER_PASS');
'''
        r=subprocess.run([str(managed_node()),'--input-type=module','-e',js],cwd=TOOL/'phase9-web',input=json.dumps(self.view),text=True,capture_output=True,timeout=30,env=tool_environment())
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(r.stdout.strip(),'CRG2b_BROWSER_PASS')


if __name__=='__main__':unittest.main()
