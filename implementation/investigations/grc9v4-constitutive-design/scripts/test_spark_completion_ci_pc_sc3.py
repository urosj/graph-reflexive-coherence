"""Accepted C_CI_PC provenance, exact metadata succession and public-surface pressure."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
import subprocess
import unittest
from unittest.mock import patch
import check_spark_completion_ci_pc_sc3 as check
from grcv4_explorer import spark_cipc as pc
from grcv4_explorer import spark_pc as prior
from grcv4_explorer import spark_cipc_research as research
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.forensic import contract_provenance
from grcv4_explorer.tooling import managed_node,tool_environment

ROOT,SIDE=check.ROOT,check.SIDE
TOOL=SIDE/'tool'


class PCSC3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.view=pc.spark_cipc_authority(ROOT,SIDE)

    def test_conditional_authority_and_immutable_predecessor_graph(self):
        self.assertEqual(check.check()['scientific_families'],['C_OS','C_CI','C_PC','C_CI_PC'])
        old=prior.load_spark_pc_forensic_context(ROOT,SIDE)
        new=pc.load_spark_cipc_forensic_context(ROOT,SIDE)
        self.assertTrue(all(new.nodes[k]==v for k,v in old.nodes.items()))
        for contract in ['SC-CCIPC-EC-DOMAIN','SC-CCIPC-EC-FULL-STATE-RETURN','SC-CCIPC-EC-COMPLETION']:
            trace=contract_provenance(new,contract)
            self.assertEqual(trace['rows'][0]['payload']['support_disposition'],['accepted_bounded_conditional_science'])
            with self.assertRaises(KeyError):contract_provenance(old,contract)
        self.assertEqual(contract_provenance(new,'SC-CCI-EC-COMPLETION')['rows'][0],
                         contract_provenance(old,'SC-CCI-EC-COMPLETION')['rows'][0])
        forward=[r for r in self.view['debts'][0]['rows'] if r['classification']=='forward_verification_routing']
        self.assertEqual(len(forward),2)
        self.assertTrue(all(r['payload']['status']=='pending_forward' for r in forward))
        self.assertEqual(sum(r['status']=='not_yet_investigated' for r in self.view['family_dispositions']),6)
        self.assertFalse(self.view['scope']['native_completed_spark_support'])

    def test_rehashed_promotion_missing_carriers_and_review_limits_reject(self):
        original=pc.load_json_object
        for defect in ('native','all_ten','claim_class','carrier','debt','review','manifest','admission'):
            def altered(path):
                v=deepcopy(original(path))
                if path==ROOT/pc.SOURCE:
                    if defect=='native':v['scope']['native_completed_spark_support']=True
                    if defect=='all_ten':v['family_dispositions'][4]['status']='accepted_bounded_scientific'
                    if defect=='claim_class':v['claims'][0]['claim_class']='normative'
                    if defect=='carrier':v['contracts'][1]['normative_equation_or_contract']='A C-only trap suffices.'
                    if defect=='debt':v['debts'][0]['remaining_work']=[]
                if path.name=='CCIPCScientificAcceptance.json' and defect=='review':v['review_limits']=[]
                if path==ROOT/pc.MANIFEST and defect=='manifest':v['chain'].pop()
                if path.name==pc.ADMISSION and defect=='admission':v['graph_digest']='0'*64
                if 'record_digest' in v:v['record_digest']=record_digest(v,'record_digest')
                return v
            with self.subTest(defect=defect),patch.object(pc,'load_json_object',altered):
                with self.assertRaises(SourceAdmissionError):pc.spark_cipc_authority(ROOT,SIDE)
        with self.assertRaises(KeyError):pc.spark_cipc_source(ROOT,SIDE,'../outside')

    def test_exact_metadata_successor_and_historical_research_flags(self):
        epochs=pc.checked_metadata_successor(ROOT)
        self.assertEqual(len(epochs['sources']),10)
        original=pc.subprocess.check_output
        def wrong_git(args,*a,**kw):
            value=original(args,*a,**kw)
            if args[:2]==['git','show'] and args[2].startswith(pc.REVIEWED_COMMIT+':'):
                return value+b'changed'
            return value
        with patch.object(pc.subprocess,'check_output',wrong_git),self.assertRaises(SourceAdmissionError):
            pc.checked_metadata_successor(ROOT)
        old=research.spark_cipc_research_status(ROOT,SIDE)
        self.assertEqual(old['report']['status'],'demonstrated_bounded_pending_review')
        self.assertFalse(old['report']['accepted_authority'])
        self.assertEqual(self.view['scope']['scientific_families'],['C_OS','C_CI','C_PC','C_CI_PC'])

    def test_historical_helper_source_has_reviewed_bytes_and_current_successor(self):
        import hashlib
        from grcv4_explorer import spark_cipc_sc3_metadata as epochs
        ref=next(r for r in research.spark_cipc_research_status(ROOT,SIDE)['source_refs']
                 if r['path']==epochs.HISTORICAL_HELPER)
        data,row=research.spark_cipc_research_source(ROOT,SIDE,ref['path'])
        self.assertEqual(hashlib.sha256(data).hexdigest(),ref['sha256'])
        self.assertEqual(data,subprocess.check_output(['git','show',epochs.REVIEWED_COMMIT+':'+ref['path']],cwd=ROOT))
        self.assertNotEqual(data,(ROOT/ref['path']).read_bytes())
        self.assertEqual(pc.spark_cipc_source(ROOT,SIDE,ref['path'])[0],data)
        with self.assertRaises(SourceAdmissionError):epochs.reviewed_source_bytes(ROOT,ref['path'],'0'*64)
        with self.assertRaises(SourceAdmissionError):epochs.reviewed_source_bytes(ROOT,'specs/grc-v4-spec.md','0'*64)

    def test_http_indexed_sources_and_failed_refresh(self):
        spec=importlib.util.spec_from_file_location('cpc_sc3_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        h=server.Handler.__new__(server.Handler);codes=[]
        h.send_response=codes.append;h.send_header=lambda *a:None;h.end_headers=lambda:None
        h.path='/api/spark-completion/applicability/ci-pc';h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],200);self.assertEqual(json.loads(h.wfile.getvalue()),self.view)
        with patch.object(server,'spark_cipc_authority',side_effect=SourceAdmissionError('held')):
            h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],503);self.assertEqual(set(json.loads(h.wfile.getvalue())),{'error'})
        h.path+='?family=C_CI_PC';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],404)
        h.path='/api/spark-completion/applicability/ci-pc/source?path=specs%2Fgrc-9-v4-spark-completion-ci-pc.md'
        h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(ROOT/'specs/grc-9-v4-spark-completion-ci-pc.md').read_bytes())
        h.path='/spark-cipc.js';h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(TOOL/'phase9-web/spark-cipc.js').read_bytes())

    def test_real_notebook_clears_stale_output(self):
        book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(c for c in book['cells'] if c.get('id')=='spark-completion-ci-pc-accepted')
        code=compile(''.join(cell['source']),'cpc-sc3-notebook','exec');ns={'repo_root':ROOT}
        exec(code,ns);self.assertEqual(ns['phase9_spark_cipc'],self.view)
        with patch.object(pc,'spark_cipc_authority',side_effect=SourceAdmissionError('held')):
            with self.assertRaises(SourceAdmissionError):exec(code,ns)
        self.assertIsNone(ns['phase9_spark_cipc'])

    def test_browser_accepted_scope_and_failed_refresh(self):
        js=r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalBasin} from './basin.js';
import {checkedSparkCIPC,sparkCIPCLoader} from './spark-cipc.js';
const v=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedSparkCIPC(v),v);
for(const edit of [x=>x.scope.native_completed_spark_support=true,
 x=>x.scope.scientific_families.push('A_OS'),x=>x.review_limits=[],x=>x.claims.pop(),x=>x.scope.G4_accepted=true]) {
 const b=structuredClone(v);edit(b);delete b.projection_digest;
 b.projection_digest=createHash('sha256').update(canonicalBasin(b)).digest('hex');
 await assert.rejects(checkedSparkCIPC(b));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=sparkCIPCLoader(output,status,async()=>({ok,json:async()=>v}),tag=>({tag,append(){}}));
await load();assert.ok(output.children.length>20);assert.match(status.textContent,/Native work remains separate/);
assert.ok(output.children.some(e=>e.textContent.includes('C_CI_PC · accepted_bounded_scientific')));
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
assert.match(readFileSync('index.html','utf8'),/id="spark-cipc-refresh"/);
console.log('CCIPC_SC3_BROWSER_PASS');
'''
        r=subprocess.run([str(managed_node()),'--input-type=module','-e',js],cwd=TOOL/'phase9-web',
            input=json.dumps(self.view),text=True,capture_output=True,timeout=30,env=tool_environment())
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(r.stdout.strip(),'CCIPC_SC3_BROWSER_PASS')


if __name__=='__main__':unittest.main()
