"""Actual HTTP/static/notebook/browser access, no native numerical runs."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import p9102_verification as checker
import p9102_acceptance as acceptance

ROOT = checker.ROOT
TOOL = ROOT / 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool'
sys.path.insert(0, str(TOOL / 'src'))
from grcv4_explorer import tranche10_verification as api
from grcv4_explorer.phase9_verification import _profile_next_gate
from grcv4_explorer.tooling import managed_node, tool_environment


class SurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with checker.no_native_runs():
            cls.evidence = checker.check()
            with patch.object(checker, 'check', return_value=cls.evidence):
                cls.value = acceptance.status()

    def test_http_sources_notebook_and_failure_clearing(self):
        spec = importlib.util.spec_from_file_location('p9102_server', TOOL / 'scripts/serve_phase9.py')
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)

        def get(path):
            h = server.Handler.__new__(server.Handler)
            h.path, h.wfile = path, BytesIO()
            codes = []
            h.send_response = codes.append
            h.send_header = lambda *args: None
            h.end_headers = lambda: None
            h.do_GET()
            return codes[-1], h.wfile.getvalue()

        # Authenticate once, then test transport of that exact checked object.
        with patch.object(checker, 'check', return_value=self.evidence):
            code, raw = get('/api/tranche10/verification')
            self.assertEqual(code, 200)
            self.assertEqual(json.loads(raw), self.value)
            code, raw = get('/api/tranche10/verification/source?path=' + checker.PATH)
            self.assertEqual(code, 200)
            self.assertEqual(raw, (ROOT / checker.PATH).read_bytes())
            code, raw = get('/api/tranche10/verification/source?path=' + acceptance.PATH)
            self.assertEqual(code, 200)
            self.assertEqual(raw, (ROOT / acceptance.PATH).read_bytes())
            self.assertEqual(get('/api/tranche10/verification/source?path=../secret')[0], 404)
            self.assertEqual(get('/api/tranche10/verification?family=A_OS')[0], 404)
            code, raw = get('/tranche10-verification.js')
            self.assertEqual(code, 200)
            self.assertEqual(raw, (TOOL / 'phase9-web/tranche10-verification.js').read_bytes())
            book = json.loads((TOOL / 'notebooks/phase9_verification.ipynb').read_text())
            cell = next(c for c in book['cells'] if c.get('id') == 'p9102-verification')
            ns = dict(repo_root=ROOT)
            exec(''.join(cell['source']), ns)
            self.assertEqual(ns['phase9_retained_verification'], self.value)
            with patch.object(api, 'tranche10_verification_status', side_effect=ValueError('drift')):
                with self.assertRaises(ValueError):
                    exec(''.join(cell['source']), ns)
                self.assertIsNone(ns['phase9_retained_verification'])
        with patch.object(server, 'tranche10_verification_status', side_effect=ValueError('drift')):
            self.assertEqual(get('/api/tranche10/verification')[0], 503)
        self.assertEqual(_profile_next_gate(dict(arg2b_work={'next_work':'old'},
                                                tranche10_verification=self.value)), self.value['next_work'])

    def test_browser_scope_and_stale_output(self):
        js = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {checkedVerification,verificationLoader} from './tranche10-verification.js';
import {canonical} from './verification.js';
const v=JSON.parse(readFileSync(0,'utf8'));
assert.equal((await checkedVerification(v)).native_steps,0);
for(const change of [x=>x.user_accepted=false,x=>x.families.push('A_OS'),x=>x.native_replays=4,
 x=>x.all_ten_P9_10_2_closed=true,
 x=>x.families_checked[0].exact_CI_root_signs_claimed=true]){
 const bad=structuredClone(v);change(bad);const {record_digest,...body}=bad;
 bad.record_digest=createHash('sha256').update(canonical(body)).digest('hex');
 await assert.rejects(()=>checkedVerification(bad));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}};
const status={textContent:''};let ok=true;
const load=verificationLoader(output,status,async()=>({ok,json:async()=>v}),tag=>({tag,textContent:''}));
await load();assert.equal(output.children.filter(e=>e.tag==='h3').length,4);
assert.match(status.textContent,/Accepted within the four-family scope/);
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
assert.match(readFileSync('index.html','utf8'),/id="tranche10-verification-refresh"/);
"""
        result = subprocess.run([str(managed_node()), '--input-type=module', '-e', js],
            input=json.dumps(self.value), text=True, capture_output=True,
            cwd=TOOL / 'phase9-web', timeout=30, env=tool_environment())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_acceptance_cannot_widen_or_relabel_evidence(self):
        path = ROOT / acceptance.PATH
        original = json.loads(path.read_bytes())
        read = Path.read_bytes
        for key, value in (('families', ['A_OS']), ('all_ten_P9_10_2_closed', True),
                           ('G4_accepted', True), ('user_accepted', False)):
            changed = checker.seal(dict(original, **{key: value}))
            with self.subTest(key=key), patch.object(Path, 'read_bytes', lambda p:
                    json.dumps(changed).encode() if p == path else read(p)):
                with self.assertRaises(ValueError):
                    acceptance.decision(ROOT, self.evidence)
        self.assertFalse(self.evidence['user_accepted'])
        self.assertFalse(self.evidence['P9_10_2_closed'])
        self.assertTrue(self.value['user_accepted'])


if __name__ == '__main__':
    unittest.main()
