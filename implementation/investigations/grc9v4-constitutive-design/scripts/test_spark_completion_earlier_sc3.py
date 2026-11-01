"""Formal endpoint adoption, immutable history and read-only inspection surfaces."""
from copy import deepcopy
from io import BytesIO
import hashlib
import importlib.util
import json
import re
import subprocess
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import check_spark_completion_earlier_sc3 as check
from grcv4_explorer import spark_earlier_accepted as accepted
from grcv4_explorer import spark_earlier_sc3_metadata as metadata
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node, tool_environment

ROOT, SIDE = check.ROOT, check.SIDE
TOOL = SIDE / 'tool'


class EarlierAdoptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.view = accepted.spark_earlier_authority(ROOT, SIDE)

    def test_adopted_contracts_counts_time_and_scope(self):
        rows = self.view['endpoints']
        self.assertEqual([r['current_completion'] for r in rows], [376, 376, 376, 376, 377])
        self.assertEqual([r['reset_completion'] for r in rows], [377, 377, 377, 377, 374])
        self.assertEqual([r['full_dimension'] for r in rows], [14, 14, 60, 60, 30])
        self.assertTrue(all(r['status'] == 'accepted_bounded_scientific' for r in rows))
        self.assertFalse(self.view['scope']['native_completed_spark_support'])
        self.assertEqual(self.view['scope']['additional_event_gain'], 0)
        self.assertEqual(check.check()['projection_digest'], self.view['projection_digest'])

    def test_rehashed_scope_endpoint_contract_and_ledger_tampering_rejected(self):
        original = accepted.load_json_object
        cases = [(accepted.SOURCE, 'count'), (accepted.SOURCE, 'native'),
                 (accepted.SOURCE, 'gain'), (accepted.MANIFEST, 'contract'),
                 (accepted.LEDGER, 'ledger'), (accepted.RECONCILIATION, 'reconciliation')]
        for path, defect in cases:
            def changed(p):
                value = deepcopy(original(p))
                if p == ROOT / path:
                    if defect == 'count': value['endpoints'][0]['current_completion'] = 100
                    elif defect == 'native': value['scope']['native_completed_spark_support'] = True
                    elif defect == 'gain': value['scope']['additional_event_gain'] = 1
                    elif defect == 'contract': value['contract_ids'].pop()
                    elif defect == 'ledger': value['claims'].pop()
                    else: value['scope']['G4_accepted'] = True
                    value['record_digest'] = record_digest(value, 'record_digest')
                return value
            with self.subTest(defect=defect), patch.object(accepted, 'load_json_object', changed), self.assertRaises(SourceAdmissionError):
                accepted.spark_earlier_authority(ROOT, SIDE)

    def test_finite_metadata_and_historical_source_download(self):
        epoch = metadata.checked_epoch(ROOT)
        self.assertEqual({r['path'] for r in epoch['sources']}, metadata.PATHS)
        original = metadata.load_json_object
        for defect in ('preimage', 'postimage', 'roster'):
            def changed(path):
                value = deepcopy(original(path))
                if path == ROOT / metadata.SOURCE:
                    if defect == 'roster': value['sources'].pop()
                    else: value['sources'][0]['before_sha256' if defect == 'preimage' else 'after_sha256'] = '0' * 64
                    value['record_digest'] = record_digest(value, 'record_digest')
                return value
            with self.subTest(defect=defect), patch.object(metadata, 'load_json_object', changed), self.assertRaises(SourceAdmissionError):
                metadata.checked_epoch(ROOT)
        from grcv4_explorer.spark_earlier_c import spark_earlier_c_source
        content, ref = spark_earlier_c_source(ROOT, SIDE, metadata.HISTORICAL_HELPER)
        self.assertEqual(hashlib.sha256(content).hexdigest(), ref['sha256'])
        self.assertNotEqual(content, (ROOT / metadata.HISTORICAL_HELPER).read_bytes())
        self.assertEqual(content, subprocess.check_output(['git', 'show', metadata.BASELINE + ':' + metadata.HISTORICAL_HELPER], cwd=ROOT))

    def test_initial_authorities_and_research_bytes_unchanged(self):
        for row in self.view['endpoints']:
            for ref in (row['research'], row['predecessor_authority']):
                before = subprocess.check_output(['git', 'show', metadata.BASELINE + ':' + ref['path']], cwd=ROOT)
                self.assertEqual(before, (ROOT / ref['path']).read_bytes())
        self.assertEqual(self.view['original_research_projections'], {
            'C': '3eecf3e0ada74250314b53e18ddbd54b0a856ab6319db7946702f17fe9f69ca3',
            'A_OS': '7b2ebfe5b2f8bcad90c0fc3d69aa5d4e86dad3c5ec165301938f4d617ccf116a'})

    def test_http_inspection_download_and_failure(self):
        spec = importlib.util.spec_from_file_location('adopted_earlier_server', TOOL / 'scripts/serve_phase9.py')
        server = importlib.util.module_from_spec(spec); spec.loader.exec_module(server)
        h = server.Handler.__new__(server.Handler); codes = []; h.command = 'GET'
        h.send_response = lambda code, message=None: codes.append(code)
        h.send_header = lambda *a: None; h.end_headers = lambda: None
        h.path = '/api/spark-completion/applicability/earlier-accepted'; h.wfile = BytesIO(); h.do_GET()
        self.assertEqual(codes[-1], 200); self.assertEqual(json.loads(h.wfile.getvalue()), self.view)
        with patch.object(server, 'spark_earlier_authority', side_effect=SourceAdmissionError('held')):
            h.wfile = BytesIO(); h.do_GET()
        self.assertEqual(codes[-1], 503); self.assertEqual(set(json.loads(h.wfile.getvalue())), {'error'})
        h.path += '?family=C_OS'; h.wfile = BytesIO(); h.do_GET(); self.assertEqual(codes[-1], 404)
        h.path = '/api/spark-completion/applicability/earlier-accepted/source?path=' + accepted.SOURCE
        h.wfile = BytesIO(); h.do_GET(); self.assertEqual(codes[-1], 200)
        self.assertEqual(h.wfile.getvalue(), (ROOT / accepted.SOURCE).read_bytes())
        with self.assertRaises(KeyError): accepted.spark_earlier_source(ROOT, SIDE, '../private')
        h.path = '/spark-earlier-accepted.js'; h.wfile = BytesIO(); h.do_GET()
        self.assertEqual(codes[-1], 200)
        self.assertEqual(h.wfile.getvalue(), (TOOL / 'phase9-web/spark-earlier-accepted.js').read_bytes())

    def test_notebook_clears_stale_accepted_result(self):
        book = json.loads((TOOL / 'notebooks/phase9_verification.ipynb').read_text())
        cell = next(c for c in book['cells'] if c.get('id') == 'spark-completion-earlier-accepted')
        ns = dict(repo_root=ROOT); code = compile(''.join(cell['source']), 'accepted-earlier-notebook', 'exec')
        exec(code, ns); self.assertEqual(ns['phase9_spark_earlier_accepted'], self.view)
        with patch.object(accepted, 'spark_earlier_authority', side_effect=SourceAdmissionError('held')), self.assertRaises(SourceAdmissionError):
            exec(code, ns)
        self.assertIsNone(ns['phase9_spark_earlier_accepted'])

    def test_publication_routes_match_adopted_documents_and_reject_drift(self):
        from grcv4_explorer import spark_publication as publication
        spec = importlib.util.spec_from_file_location('spark_publication_server', TOOL / 'scripts/serve_phase9.py')
        server = importlib.util.module_from_spec(spec); spec.loader.exec_module(server)
        h = server.Handler.__new__(server.Handler); codes = []; headers = {}; h.command = 'GET'
        h.send_response = lambda code, message=None: codes.append(code)
        h.send_header = lambda key, value: headers.update({key: value})
        h.end_headers = lambda: None
        for path in publication.DOCUMENTS:
            h.path = '/api/spark-completion/publication/source?path=' + path
            h.wfile = BytesIO(); h.do_GET()
            self.assertEqual(codes[-1], 200)
            self.assertEqual(h.wfile.getvalue(), (ROOT / path).read_bytes())
            self.assertEqual(headers['X-Evidence-SHA256'], hashlib.sha256(h.wfile.getvalue()).hexdigest())
        for path in ('../private', publication.INV + 'drafts/spark-completion/Paper.md', accepted.SOURCE):
            h.path = '/api/spark-completion/publication/source?path=' + path
            h.wfile = BytesIO(); h.do_GET(); self.assertEqual(codes[-1], 404)
        h.path = '/api/spark-completion/publication/source?path=' + publication.INV + 'drafts/2026-11-GRC-V4.md'
        original = publication.load_json_object
        for defect in ('hash', 'missing', 'review_status'):
            def changed(path):
                value = deepcopy(original(path)); editorial = value['editorial_consolidation']
                if defect == 'review_status': editorial['manuscript_succession']['review_status'] = 'pending'
                elif defect == 'missing': editorial['documents'] = []
                else:
                    for row in editorial['documents']: row['sha256'] = '0' * 64
                value['record_digest'] = record_digest(value, 'record_digest')
                return value
            with self.subTest(defect=defect), patch.object(publication, 'load_json_object', changed):
                h.wfile = BytesIO(); h.do_GET(); self.assertEqual(codes[-1], 503)
                self.assertEqual(set(json.loads(h.wfile.getvalue())), {'error'})

        page = (TOOL / 'phase9-web/index.html').read_text()
        links = [url for url in re.findall(r'href="([^"]+)"', page)
                 if url.startswith('/api/spark-completion/publication/source?')]
        self.assertEqual({parse_qs(urlsplit(url).query)['path'][0] for url in links}, publication.DOCUMENTS)
        self.assertIn('The corrected manuscript and proposal are adopted', page)
        book = json.loads((TOOL / 'notebooks/phase9_verification.ipynb').read_text())
        cell = next(c for c in book['cells'] if c.get('id') == 'spark-publication-reading')
        self.assertEqual(cell['cell_type'], 'markdown')
        self.assertIn('the corrected manuscript and proposal are adopted', ''.join(cell['source']))
        for target in re.findall(r'\]\(([^)]+)\)', ''.join(cell['source'])):
            self.assertTrue((TOOL / 'notebooks' / target).resolve().is_file(), target)

    def test_browser_integrity_primary_results_and_stale_refresh(self):
        js = r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalBasin} from './basin.js';
import {checkedSparkEarlierAccepted,sparkEarlierAcceptedLoader} from './spark-earlier-accepted.js';
const v=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedSparkEarlierAccepted(v),v);
for(const edit of [x=>x.scope.native_completed_spark_support=true,x=>x.endpoints[0].current_completion=100,x=>x.scope.additional_event_gain=1]){
 const b=structuredClone(v);edit(b);delete b.projection_digest;
 b.projection_digest=createHash('sha256').update(canonicalBasin(b)).digest('hex');
 await assert.rejects(checkedSparkEarlierAccepted(b));
}
const create=tag=>({tag,children:[],append(e){this.children.push(e)}});
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};let ok=true;
const load=sparkEarlierAcceptedLoader(output,status,async()=>({ok,json:async()=>v}),create);
await load();assert.match(status.textContent,/contracts verified/);
const table=output.children.find(e=>e.tag==='table');assert.equal(table.children.length,6);
assert.equal(table.children[1].children[1].textContent,'374 → 376');
assert.equal(table.children[5].children[1].textContent,'375 → 377');
assert.ok(output.children.find(e=>e.tag==='details'));
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
let resolveFirst,calls=0;
const stale=sparkEarlierAcceptedLoader(output,status,()=>++calls===1?new Promise(resolve=>resolveFirst=resolve):Promise.resolve({ok:true,json:async()=>v}),create);
const first=stale();await stale();const kept=output.children;resolveFirst({ok:false});await first;
assert.equal(output.children,kept);assert.match(status.textContent,/contracts verified/);
const page=readFileSync('index.html','utf8');
assert.ok(page.indexOf('id="spark-earlier-accepted-refresh"')<page.indexOf('id="spark-completion-refresh"'));
console.log('EARLIER_ACCEPTED_BROWSER_PASS');
'''
        result = subprocess.run([str(managed_node()), '--input-type=module', '-e', js], cwd=TOOL / 'phase9-web',
                                input=json.dumps(self.view), text=True, capture_output=True, timeout=30, env=tool_environment())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'EARLIER_ACCEPTED_BROWSER_PASS')


if __name__ == '__main__':
    unittest.main(verbosity=2)
