"""Earlier-domain inspection, provenance, accounting and failed-refresh checks."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import importlib.util,json,subprocess,sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
SIDE=ROOT/INV/'tools/exploratory-side-tool';TOOL=SIDE/'tool'
sys.path.insert(0,str(TOOL/'src'))
from grcv4_explorer import spark_aos_earlier as research,spark_aos_earlier_metadata as epochs
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node,tool_environment


class EarlierSurfaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.view=research.spark_aos_earlier_status(ROOT,SIDE)

    def test_report_accounting_and_rehashed_changes_reject(self):
        r=self.view['report'];self.assertFalse(r['accepted_authority'])
        self.assertEqual([r['decisions'][x]['anisotropic_window_end'] for x in ('current','reset')],[377,374])
        self.assertTrue(all(d['additional_event_gain']==0 for d in r['decisions'].values()))
        original=research.load_json_object
        for field,value in [('accepted_authority',True),('relative_dimension',14),('additional_event_gain',1),
                            ('native_completion',True),('review_limits',[]),('checks_record_digest','0'*64)]:
            def altered(path):
                v=deepcopy(original(path))
                if path==ROOT/research.REPORT:v[field]=value;v['record_digest']=record_digest(v,'record_digest')
                return v
            with self.subTest(field=field),patch.object(research,'load_json_object',altered),self.assertRaises(SourceAdmissionError):
                research.spark_aos_earlier_status(ROOT,SIDE)
        bound=research._bound_file
        def drift(root,path,digest):
            if path.endswith('AOS-current.json.xz'):raise SourceAdmissionError('changed trajectory')
            return bound(root,path,digest)
        with patch.object(research,'_bound_file',drift),self.assertRaises(SourceAdmissionError):research.spark_aos_earlier_status(ROOT,SIDE)

    def test_finite_metadata_rejects_preimage_and_path_widening(self):
        self.assertEqual(len(epochs.checked_epoch(ROOT)['sources']),9)
        original=epochs.load_json_object
        def altered(path):
            v=deepcopy(original(path));v['sources'].pop();v['record_digest']=record_digest(v,'record_digest');return v
        with patch.object(epochs,'load_json_object',altered),self.assertRaises(SourceAdmissionError):epochs.checked_epoch(ROOT)
        with patch.object(epochs.subprocess,'check_output',return_value=b'wrong'),self.assertRaises(SourceAdmissionError):epochs.checked_epoch(ROOT)
        with self.assertRaises(SourceAdmissionError):epochs.bound_metadata_files(ROOT,{'specs/grc-v4-spec.md':'0'*64})

    def test_http_source_and_failed_refresh(self):
        spec=importlib.util.spec_from_file_location('earlier_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        h=server.Handler.__new__(server.Handler);codes=[]
        h.send_response=codes.append;h.send_header=lambda *a:None;h.end_headers=lambda:None
        h.path='/api/spark-completion/applicability/a-os/earlier';h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],200);self.assertEqual(json.loads(h.wfile.getvalue()),self.view)
        with patch.object(server,'spark_aos_earlier_status',side_effect=SourceAdmissionError('held')):
            h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],503);self.assertEqual(set(json.loads(h.wfile.getvalue())),{'error'})
        h.path+='?family=A_OS';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],404)
        h.path='/api/spark-completion/applicability/a-os/earlier/source?path='+research.CHECKS
        h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(ROOT/research.CHECKS).read_bytes())
        with self.assertRaises(KeyError):research.spark_aos_earlier_source(ROOT,SIDE,'../outside')

    def test_notebook_clears_stale_output(self):
        book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(c for c in book['cells'] if c.get('id')=='spark-completion-a-os-earlier')
        code=compile(''.join(cell['source']),'earlier-notebook','exec');ns={'repo_root':ROOT}
        exec(code,ns);self.assertEqual(ns['phase9_spark_aos_earlier'],self.view)
        with patch.object(research,'spark_aos_earlier_status',side_effect=SourceAdmissionError('held')):
            with self.assertRaises(SourceAdmissionError):exec(code,ns)
        self.assertIsNone(ns['phase9_spark_aos_earlier'])

    def test_browser_scope_and_stale_refresh(self):
        js=r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalBasin} from './basin.js';
import {checkedSparkAOSEarlier,sparkAOSEarlierLoader} from './spark-aos-earlier.js';
const v=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedSparkAOSEarlier(v),v);
for(const edit of [x=>x.report.accepted_authority=true,x=>x.report.additional_event_gain=1,
 x=>x.report.relative_dimension=14,x=>x.report.decisions.current.anisotropic_entry=92]) {
 const b=structuredClone(v);edit(b);delete b.report.record_digest;
 b.report.record_digest=createHash('sha256').update(canonicalBasin(b.report)).digest('hex');
 b.report_record_digest=b.report.record_digest;delete b.projection_digest;
 b.projection_digest=createHash('sha256').update(canonicalBasin(b)).digest('hex');
 await assert.rejects(checkedSparkAOSEarlier(b));
}
const create=tag=>({tag,children:[],append(e){this.children.push(e)}});
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=sparkAOSEarlierLoader(output,status,async()=>({ok,json:async()=>v}),create);
await load();assert.ok(output.children.length>10);assert.match(status.textContent,/Review pending/);
assert.ok(output.children.some(e=>e.tag==='table'&&e.children.length===3));
ok=false;await load();assert.equal(output.children.length,0);
assert.match(status.textContent,/unavailable/);
let resolve;
const race=sparkAOSEarlierLoader(output,status,()=>new Promise(r=>{resolve=r}),create);
const first=race();const old=resolve;const second=race();resolve({ok:false});await second;
old({ok:true,json:async()=>v});await first;assert.equal(output.children.length,0);
assert.match(readFileSync('index.html','utf8'),/id="spark-aos-earlier-refresh"/);
console.log('AOS_EARLIER_BROWSER_PASS');
'''
        r=subprocess.run([str(managed_node()),'--input-type=module','-e',js],cwd=TOOL/'phase9-web',
            input=json.dumps(self.view),text=True,capture_output=True,timeout=30,env=tool_environment())
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(r.stdout.strip(),'AOS_EARLIER_BROWSER_PASS')

    def test_accepted_and_historical_projections_preserved(self):
        from grcv4_explorer.spark_aos import spark_aos_authority
        from grcv4_explorer.spark_aos_research import spark_aos_research_status
        accepted=spark_aos_authority(ROOT,SIDE)
        self.assertEqual(accepted['projection_digest'],'5006a5e76811aed03c41c32088cb5775068f6247dfaf3a4640c10e3d93704afb')
        self.assertEqual(accepted['scope']['scientific_families'],['C_OS','C_CI','C_PC','C_CI_PC','A_OS'])
        old=spark_aos_research_status(ROOT,SIDE)
        self.assertEqual(old['projection_digest'],'a96cfbe550a3dd59f8d8797b0cdf068914274403561f37aae68fab6354ae8f0f')
        self.assertEqual(old['report']['decisions']['current']['target_completion_step'],1041)
        self.assertFalse(old['report']['accepted_authority'])


if __name__=='__main__':unittest.main()
