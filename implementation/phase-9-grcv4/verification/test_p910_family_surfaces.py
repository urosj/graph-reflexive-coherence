"""Family evidence access, scope pressure and preserved historical source bytes."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import p910_family_basin as campaign
import p910_basin_source_epoch as epoch
import p910_family_acceptance as acceptance

ROOT = campaign.ROOT
TOOL = ROOT / 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool'
sys.path.insert(0, str(TOOL / 'src'))
from grcv4_explorer import tranche10_families as api
from grcv4_explorer.phase9_verification import _profile_next_gate
from grcv4_explorer.tooling import managed_node, tool_environment


class FamilySurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with campaign.v.no_native_runs():
            cls.evidence = campaign.check()
        with patch.object(campaign, 'check', return_value=cls.evidence):
            cls.view = api.family_basin_status(ROOT)

    def test_http_notebook_source_and_scope(self):
        spec = importlib.util.spec_from_file_location('family_basin_server', TOOL / 'scripts/serve_phase9.py')
        server = importlib.util.module_from_spec(spec); spec.loader.exec_module(server)

        def get(path):
            h = server.Handler.__new__(server.Handler)
            h.path, h.wfile = path, BytesIO(); codes = []
            h.send_response = codes.append; h.send_header = lambda *a: None; h.end_headers = lambda: None
            h.do_GET(); return codes[-1], h.wfile.getvalue()

        with patch.object(campaign, 'check', return_value=self.evidence):
            status, raw = get('/api/tranche10/families?family=A_OS')
            self.assertEqual(status, 200); self.assertEqual(json.loads(raw), self.view)
            for ref in self.view['evidence']:
                status, raw = get('/api/tranche10/families/source?family=A_OS&path='+ref['path'])
                self.assertEqual(status, 200); self.assertEqual(raw, (ROOT/ref['path']).read_bytes())
            for path in ('/api/tranche10/families?family=A_CI_PC', '/api/tranche10/families',
                         '/api/tranche10/families?family=A_OS&family=C_OS',
                         '/api/tranche10/families/source?family=A_OS&path=../secret'):
                self.assertEqual(get(path)[0], 404)
            self.assertEqual(get('/tranche10-families.js')[0], 200)
            book = json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
            cell = next(c for c in book['cells'] if c.get('id') == 'p910-family-basin')
            ns = dict(repo_root=ROOT); exec(''.join(cell['source']), ns)
            self.assertEqual(ns['phase9_family_basin'], self.view)
            with patch.object(api, 'family_basin_status', side_effect=ValueError('drift')):
                with self.assertRaises(ValueError): exec(''.join(cell['source']), ns)
                self.assertIsNone(ns['phase9_family_basin'])
        with patch.object(server, 'family_basin_status', side_effect=ValueError('drift')):
            self.assertEqual(get('/api/tranche10/families?family=A_OS')[0], 503)
        self.assertEqual(_profile_next_gate(dict(tranche10_family=self.view,
                            tranche10_verification={'next_work':'old'})), self.view['next_work'])

    def test_exact_history_separation_and_finite_source_preimage(self):
        cases = self.evidence['direct_target']['observations']
        source = cases[0]['saved_native_state']['inputs']
        returned = cases[1]['saved_native_state']['inputs']
        self.assertEqual(source['current'], source['reset'])
        self.assertNotEqual(returned['current']['C'], returned['reset']['C'])
        self.assertNotEqual(returned['current']['W_A'], returned['reset']['W_A'])
        self.assertTrue(epoch.first_group_unchanged(ROOT))
        name = 'src/pygrc/models/grc_9_v4_basin.py'
        old = epoch.original(ROOT, name)
        raw, ref = epoch.read_source(ROOT, dict(path=name, sha256=epoch.sha(old)))
        self.assertEqual(raw, old); self.assertEqual(ref['revision'], epoch.BASELINE)
        self.assertNotEqual(raw, (ROOT/name).read_bytes())
        read = Path.read_bytes
        with patch.object(Path, 'read_bytes', lambda p: read(p)+b'\nchanged' if p==ROOT/name else read(p)):
            with self.assertRaises(ValueError):
                epoch.peel_sha(ROOT, name, epoch.sha((ROOT/name).read_bytes()))

    def test_browser_binding_and_failure_clearing(self):
        js = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonical} from './verification.js';
import {checkedFamilyBasin,familyBasinLoader} from './tranche10-families.js';
const v=JSON.parse(readFileSync(0,'utf8'));await checkedFamilyBasin(v);
for(const change of [x=>x.family='C_PC',x=>x.user_accepted=false,x=>x.G4_accepted=true,
 x=>x.all_ten_P9_10_2_closed=true,
 x=>x.boundaries[0].role_equations.current.geometry_residual_upper='1']){
 const bad=structuredClone(v);change(bad);const {record_digest,...body}=bad;
 bad.record_digest=createHash('sha256').update(canonical(body)).digest('hex');
 await assert.rejects(()=>checkedFamilyBasin(bad));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}};
const status={textContent:''};let ok=true;
const load=familyBasinLoader(output,status,async()=>({ok,json:async()=>v}),tag=>({tag,textContent:''}));
await load('A_OS');assert.equal(output.children.filter(x=>x.tag==='h4').length,2);
assert.match(status.textContent,/Accepted within bounded A_OS scope/);
ok=false;await load('A_OS');assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
assert.match(readFileSync('index.html','utf8'),/id="tranche10-family-select"/);
"""
        result = subprocess.run([str(managed_node()), '--input-type=module', '-e', js],
            input=json.dumps(self.view), text=True, capture_output=True,
            cwd=TOOL/'phase9-web', timeout=30, env=tool_environment())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_acceptance_is_bounded_and_keeps_original_execution_flags(self):
        path = ROOT / acceptance.path('A_OS')
        original = json.loads(path.read_bytes())
        read = Path.read_bytes
        for key, value in (('family', 'C_PC'), ('user_accepted', False),
                           ('all_ten_P9_10_2_closed', True), ('G4_accepted', True)):
            changed = campaign.seal(dict(original, **{key: value}))
            with self.subTest(key=key), patch.object(Path, 'read_bytes', lambda p:
                    json.dumps(changed).encode() if p == path else read(p)):
                with self.assertRaises(ValueError):
                    acceptance.decision(ROOT, self.evidence)
        self.assertFalse(self.evidence['user_accepted'])
        self.assertFalse(self.evidence['P9_10_1_closed'])
        self.assertFalse(self.evidence['P9_10_2_closed'])
        self.assertTrue(self.view['user_accepted'])


if __name__ == '__main__':
    unittest.main()
