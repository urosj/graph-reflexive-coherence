"""Pressure exact subjects, source preservation, scope and real read-only surfaces."""
from contextlib import ExitStack
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import p9103_regressions as c

TOOL = c.ROOT / 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool'


class RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A real retained check once; all mutation tests below reuse its exact
        # authenticated inputs, without repeating the old numerical campaigns.
        with patch.object(c, 'run_group', side_effect=AssertionError('suite rerun')), c.v.no_native_runs():
            cls.value = c.check()

    def test_population_and_preserved_limits(self):
        v = self.value
        self.assertEqual(len(v['reconciliation']), 10)
        self.assertEqual(sum(x['saved_charge_checks'] for x in v['reconciliation']), 40)
        self.assertEqual(sum(x['receipts'] for x in v['reconciliation']), 530)
        self.assertEqual(sum(x['commit_groups'] for x in v['reconciliation']), 150)
        self.assertGreater(v['preservation']['unchanged_legacy_modules'], 100)
        self.assertFalse(v['user_accepted']); self.assertFalse(v['G4_accepted'])

    def test_resealed_scope_identity_roster_and_outcome_mutations(self):
        def mutate(v, kind):
            if kind == 'family': v['reconciliation'].pop()
            elif kind == 'target': v['reconciliation'][0]['subjects']['v2'] = v['reconciliation'][0]['subjects']['v1']
            elif kind == 'source': v['source_refs'][0]['sha256'] = '0'*64
            elif kind == 'release': v['preservation']['release_id'] = 'invented'
            elif kind == 'skip': v['regressions'][0]['skips'] = 1
            elif kind == 'roster': v['regressions'][0]['tests'].pop()
            else: v[kind] = True
        with ExitStack() as stack:
            for name, expected in (('source_bindings',self.value['source_refs']),
                                   ('reconciliation',self.value['reconciliation']),
                                   ('preservation',self.value['preservation'])):
                stack.enter_context(patch.object(c, name, return_value=expected))
            for kind in ('family','target','source','release','skip','roster','user_accepted','G4_accepted','P9_10_3_closed'):
                bad=deepcopy(self.value);mutate(bad,kind)
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    c.validate(c.seal(bad))

    def test_changed_production_cannot_be_relabelled_as_the_run(self):
        original = c.git
        def changed(*args):
            return b'src/pygrc/models/grc_9_v4.py\n' if args[:2] == ('diff', '--name-only') else original(*args)
        with patch.object(c,'git',side_effect=changed), self.assertRaisesRegex(ValueError,'input drift'):
            c.source_bindings()

    def test_test_successor_preserves_old_bytes_and_unrelated_assertions(self):
        import p9103_source_epoch as epoch
        name = 'tests/models/test_grc_9_v4_contracts.py'
        path = c.ROOT / name
        original = epoch.original(c.ROOT, name)
        raw, ref = epoch.read_source(c.ROOT, dict(path=name, sha256=epoch.sha(original)))
        self.assertEqual(raw, original)
        self.assertEqual(ref['basis'], 'historical_git')
        read = Path.read_bytes
        changed = read(path).replace(b'self.assertGreaterEqual(cfg.current.C[0], 0)',
                                     b'self.assertGreaterEqual(cfg.current.C[0], 1)')
        self.assertNotEqual(changed, read(path))
        with patch.object(Path, 'read_bytes', lambda p: changed if p == path else read(p)):
            with self.assertRaisesRegex(ValueError, 'unrelated assertions'):
                epoch.previous_bytes(c.ROOT, name)

    def test_api_browser_notebook_and_no_rerun_on_access(self):
        import sys
        sys.path.insert(0, str(TOOL/'src'))
        from grcv4_explorer import tranche10_regressions as api
        from grcv4_explorer.phase9_verification import _profile_next_gate
        from grcv4_explorer.tooling import managed_node, tool_environment
        spec=importlib.util.spec_from_file_location('p9103_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        def get(path):
            h=server.Handler.__new__(server.Handler);h.path=path;h.wfile=BytesIO();codes=[]
            h.send_response=codes.append;h.send_header=lambda *args:None;h.end_headers=lambda:None
            h.do_GET();return codes[-1],h.wfile.getvalue()
        with patch.object(c,'check',return_value=self.value), patch.object(c,'run_group',side_effect=AssertionError('suite rerun')):
            view=api.tranche10_regressions_status(c.ROOT)
            code,raw=get('/api/tranche10/regressions');self.assertEqual(code,200);self.assertEqual(json.loads(raw),view)
            code,raw=get('/api/tranche10/regressions/source?path='+c.PATH)
            self.assertEqual(code,200);self.assertEqual(raw,(c.ROOT/c.PATH).read_bytes())
            self.assertEqual(get('/api/tranche10/regressions/source?path=../secret')[0],404)
            self.assertEqual(get('/api/tranche10/regressions?family=A_OS')[0],404)
            self.assertEqual(get('/tranche10-regressions.js')[0],200)
            book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_text())
            cell=next(x for x in book['cells'] if x.get('id')=='p9103-regressions')
            ns=dict(repo_root=c.ROOT);exec(''.join(cell['source']),ns)
            self.assertEqual(ns['phase9_regressions'],view)
            with patch.object(api,'tranche10_regressions_status',side_effect=ValueError('drift')):
                with self.assertRaises(ValueError):exec(''.join(cell['source']),ns)
                self.assertIsNone(ns['phase9_regressions'])
        with patch.object(server,'tranche10_regressions_status',side_effect=ValueError('drift')):
            self.assertEqual(get('/api/tranche10/regressions')[0],503)
        self.assertEqual(_profile_next_gate(dict(tranche10_regressions=view,tranche10_family={'next_work':'old'})),view['next_work'])
        js="""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonical} from './verification.js';
import {checkedRegressions,regressionsLoader} from './tranche10-regressions.js';
const v=JSON.parse(readFileSync(0,'utf8'));await checkedRegressions(v);
for(const change of [x=>x.user_accepted=true,x=>x.G4_accepted=true,x=>x.families.pop(),x=>x.regressions[0].tests_run++,x=>x.reconciliation[0].subjects.v2=x.reconciliation[0].subjects.v1]){
 const b=structuredClone(v);change(b);const {record_digest,...body}=b;
 b.record_digest=createHash('sha256').update(canonical(body)).digest('hex');
 await assert.rejects(()=>checkedRegressions(b));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}};
const status={textContent:''};let ok=true;
const load=regressionsLoader(output,status,async()=>({ok,json:async()=>v}),tag=>({tag,textContent:''}));
await load();assert.equal(output.children.filter(e=>e.tag==='h4').length,10);
assert.match(status.textContent,/acceptance pending/);
ok=false;await load();assert.equal(output.children.length,0);
assert.match(status.textContent,/unavailable/);
assert.match(readFileSync('index.html','utf8'),/id="tranche10-regressions-refresh"/);
"""
        result=subprocess.run([str(managed_node()),'--input-type=module','-e',js],input=json.dumps(view),text=True,
                              capture_output=True,cwd=TOOL/'phase9-web',env=tool_environment(),timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)


if __name__ == '__main__':
    unittest.main()
