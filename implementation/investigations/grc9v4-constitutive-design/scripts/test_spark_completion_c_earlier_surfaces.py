"""Earlier comparison surfaces, finite metadata and preserved accepted authority."""
from copy import deepcopy
from io import BytesIO
import hashlib,importlib.util,json,subprocess,unittest
from unittest.mock import patch
import check_spark_completion_c_earlier_research as check
from grcv4_explorer import spark_earlier_c as research
from grcv4_explorer import spark_earlier_c_metadata as meta
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node,tool_environment
ROOT,SIDE=check.ROOT,check.SIDE;TOOL=SIDE/'tool'


class EarlierCSurfaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.view=research.spark_earlier_c_status(ROOT,SIDE)

    def test_scope_duration_and_historical_counts_are_separate(self):
        r=self.view['report'];self.assertFalse(r['accepted_authority']);self.assertEqual(r['ordinary_duration'],'32')
        self.assertEqual(len(r['comparison']),5);self.assertEqual(r['additional_event_gain'],0)
        self.assertEqual([v['earlier_current_completion']for v in r['comparison']],[376,376,376,376,377])
        self.assertEqual(r['storage']['retained_states'],3012)
        self.assertEqual(r['existing_A_OS']['current_completion'],377)
        self.assertTrue(r['original_execution_counts_preserved'])
        self.assertEqual(check.check()['projection_digest'],self.view['projection_digest'])

    def test_rehashed_promotion_duration_or_tail_reject(self):
        load=research.load_json_object
        for defect in ('authority','native','gain','duration','counts','tail','sources'):
            def changed(path):
                v=deepcopy(load(path))
                if path==ROOT/research.REPORT:
                    if defect=='authority':v['accepted_authority']=True
                    if defect=='native':v['native_completion']=True
                    if defect=='gain':v['additional_event_gain']=1
                    if defect=='duration':v['ordinary_duration']='64'
                    if defect=='counts':v['original_execution_counts_preserved']=False
                    if defect=='tail':v['supporting_trajectory_steps_after_completion']=500
                    if defect=='sources':v['sources'].pop()
                    v['record_digest']=record_digest(v,'record_digest')
                return v
            with self.subTest(defect=defect),patch.object(research,'load_json_object',changed),self.assertRaises(SourceAdmissionError):
                research.spark_earlier_c_status(ROOT,SIDE)
        with self.assertRaises(KeyError):research.spark_earlier_c_source(ROOT,SIDE,'../outside')

    def test_exact_metadata_roster_preimages_and_historical_helper(self):
        v=meta.checked_epoch(ROOT);self.assertEqual(len(v['sources']),9)
        load=meta.load_json_object
        for defect in ('preimage','postimage','path','scope'):
            def changed(path):
                data=deepcopy(load(path))
                if path==ROOT/meta.SOURCE:
                    if defect=='preimage':data['sources'][0]['before_sha256']='0'*64
                    if defect=='postimage':data['sources'][0]['after_sha256']='0'*64
                    if defect=='path':data['sources'].pop()
                    if defect=='scope':data['native_runtime_changed']=True
                    data['record_digest']=record_digest(data,'record_digest')
                return data
            with self.subTest(defect=defect),patch.object(meta,'load_json_object',changed),self.assertRaises(SourceAdmissionError):meta.checked_epoch(ROOT)
        row=next(r for r in v['sources']if r['path']==meta.HISTORICAL_HELPER)
        before=subprocess.check_output(['git','show',meta.BASELINE+':'+meta.HISTORICAL_HELPER],cwd=ROOT)
        self.assertEqual(meta.reviewed_source_bytes(ROOT,meta.HISTORICAL_HELPER,row['before_sha256']),before)
        self.assertNotEqual(before,(ROOT/meta.HISTORICAL_HELPER).read_bytes())
        original=meta.subprocess.check_output
        def wrong_git(args,*a,**kw):
            result=original(args,*a,**kw)
            return result+b'changed'if args[:3]==['git','cat-file','--batch']else result
        with patch.object(meta.subprocess,'check_output',wrong_git),self.assertRaises(SourceAdmissionError):meta.checked_epoch(ROOT)

    def test_preserved_all_ten_authority_and_existing_research_projections(self):
        from grcv4_explorer.spark_arg2b import spark_arg2b_authority
        from grcv4_explorer.spark_arg2b_research import spark_arg2b_research_status
        from grcv4_explorer.spark_aos_earlier import spark_aos_earlier_status
        accepted=spark_arg2b_authority(ROOT,SIDE)
        self.assertEqual(accepted['projection_digest'],'c3088e4da6a5c720087b3f6ab894fd636e90ec7b955e95c1b329a0006b928950')
        self.assertEqual(len(accepted['scope']['scientific_families']),10)
        self.assertFalse(accepted['scope']['native_completed_spark_support'])
        self.assertEqual(spark_arg2b_research_status(ROOT,SIDE)['projection_digest'],'a1908f8e8617501ad8c64fea39b815f0daee0798fe864f984f357ca3c6f70452')
        self.assertEqual(spark_aos_earlier_status(ROOT,SIDE)['projection_digest'],'7b2ebfe5b2f8bcad90c0fc3d69aa5d4e86dad3c5ec165301938f4d617ccf116a')

    def test_http_download_and_failed_refresh(self):
        spec=importlib.util.spec_from_file_location('earlier_c_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        h=server.Handler.__new__(server.Handler);codes=[];h.command='GET'
        h.send_response=lambda code,message=None:codes.append(code);h.send_header=lambda *a:None;h.end_headers=lambda:None
        h.path='/api/spark-completion/applicability/earlier-c';h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],200);self.assertEqual(json.loads(h.wfile.getvalue()),self.view)
        with patch.object(server,'spark_earlier_c_status',side_effect=SourceAdmissionError('held')):
            h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],503);self.assertEqual(set(json.loads(h.wfile.getvalue())),{'error'})
        h.path+='?family=C_OS';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],404)
        path=research.BASE+'COS-current-prefix.json.xz';h.path='/api/spark-completion/applicability/earlier-c/source?path='+path
        h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200);self.assertEqual(h.wfile.getvalue(),(ROOT/path).read_bytes())
        h.path='/spark-earlier-c.js';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(TOOL/'phase9-web/spark-earlier-c.js').read_bytes())

    def test_notebook_clears_stale_result(self):
        book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_text())
        cell=next(c for c in book['cells']if c.get('id')=='spark-completion-earlier-c')
        ns=dict(repo_root=ROOT);code=compile(''.join(cell['source']),'earlier-c-notebook','exec')
        exec(code,ns);self.assertEqual(ns['phase9_spark_earlier_c'],self.view)
        with patch.object(research,'spark_earlier_c_status',side_effect=SourceAdmissionError('held')),self.assertRaises(SourceAdmissionError):exec(code,ns)
        self.assertIsNone(ns['phase9_spark_earlier_c'])

    def test_browser_integrity_comparison_failure_and_stale_refresh(self):
        js=r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalBasin} from './basin.js';
import {checkedSparkEarlierC,sparkEarlierCLoader} from './spark-earlier-c.js';
const v=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedSparkEarlierC(v),v);
for(const edit of [x=>x.report.native_completion=true,x=>x.report.ordinary_duration='16',x=>x.report.additional_event_gain=1,x=>x.report.comparison.pop()]){
 const b=structuredClone(v);edit(b);delete b.projection_digest;b.projection_digest=createHash('sha256').update(canonicalBasin(b)).digest('hex');await assert.rejects(checkedSparkEarlierC(b));
}
const create=tag=>({tag,children:[],append(e){this.children.push(e)}});
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};let ok=true;
const load=sparkEarlierCLoader(output,status,async()=>({ok,json:async()=>v}),create);
await load();assert.match(status.textContent,/evidence verified/);
const table=output.children.find(e=>e.tag==='table');assert.equal(table.children.length,6);
assert.equal(table.children[1].children[2].textContent,'376');assert.equal(table.children[5].children[2].textContent,'377');
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
let resolveFirst,calls=0;
const stale=sparkEarlierCLoader(output,status,()=>++calls===1?new Promise(resolve=>resolveFirst=resolve):Promise.resolve({ok:true,json:async()=>v}),create);
const first=stale();await stale();const kept=output.children;resolveFirst({ok:false});await first;assert.equal(output.children,kept);assert.match(status.textContent,/evidence verified/);
assert.match(readFileSync('index.html','utf8'),/id="spark-earlier-c-refresh"/);console.log('EARLIER_C_BROWSER_PASS');
'''
        result=subprocess.run([str(managed_node()),'--input-type=module','-e',js],cwd=TOOL/'phase9-web',input=json.dumps(self.view),text=True,capture_output=True,timeout=30,env=tool_environment())
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'EARLIER_C_BROWSER_PASS')


if __name__=='__main__':unittest.main(verbosity=2)
