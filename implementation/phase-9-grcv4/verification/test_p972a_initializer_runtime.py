"""Read-only retained-record pressure; no numerical replay."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import unittest

import verify_p972a_initializer_runtime as runtime


class RuntimeEvidenceTests(unittest.TestCase):
    def test_retained_record_and_packaged_contract(self):
        self.assertTrue(runtime.check()['positive_migration_verified'])
        self.assertFalse(runtime.check()['aggregate_closed'])

    def test_rehashed_overclaim_and_unbound_source_reject(self):
        sources = runtime.bindings()
        value = runtime.p.read(runtime.p.ROOT / runtime.RECORD)
        for field, replacement in (('aggregate_closed', True), ('source_bindings', {}), ('test_ids', [])):
            bad = deepcopy(value)
            bad[field] = replacement
            bad['record_digest'] = runtime.p.digest_record(bad)
            with self.subTest(field=field), self.assertRaises(ValueError):
                runtime.validate(bad, sources)

    def test_rehashed_receipt_link_does_not_authenticate_pair(self):
        bad = deepcopy(runtime.p.read(runtime.p.ROOT / runtime.RECORD))
        bad['cases']['A_OS']['receipts'][0]['identity_payload']['initializer_pair_id'] = 'grcv4-a-reference-pass-pair-sha256:' + '0'*64
        bad['record_digest'] = runtime.p.digest_record(bad)
        with self.assertRaises(ValueError):
            runtime.validate(bad, runtime.bindings())

    def test_actual_status_notebook_and_http_expose_runtime_separately(self):
        root = runtime.p.ROOT
        tool = root / runtime.p.SIDE / 'tool'
        sys.path.insert(0, str(tool / 'src'))
        from grcv4_explorer.phase9_verification import verification_status
        status = verification_status(root)
        self.assertEqual(status['current_boundary'], 'passed', status.get('error'))
        self.assertEqual(status['initializer_runtime'], runtime.check())
        book = json.loads((tool / 'notebooks/phase9_verification.ipynb').read_text())
        cell = next(c for c in book['cells'] if c['id'] == 'query-status')
        namespace = dict(Path=Path, repo_root=root, PHASE9_REPO_ROOT=root,
                         PHASE9_STATUS_ONLY=True, verification_status=verification_status)
        exec(compile(''.join(cell['source']), 'phase9_verification.ipynb:query-status', 'exec'), namespace)
        self.assertEqual(namespace['phase9_status']['initializer_runtime'], status['initializer_runtime'])
        spec = importlib.util.spec_from_file_location('p972a_runtime_http', tool / 'scripts/serve_phase9.py')
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        handler.path = '/api/status'
        statuses = []
        handler.send_response = statuses.append
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(statuses, [200])
        self.assertEqual(json.loads(handler.wfile.getvalue())['initializer_runtime'], status['initializer_runtime'])
        from grcv4_explorer.tooling import managed_node, tool_environment
        code = """
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {verifiedStatus, canonical} from './verification.js';
const value = JSON.parse(readFileSync(0, 'utf8'));
assert.deepEqual(await verifiedStatus(value), value);
for (const edit of [v=>v.initializer_runtime.aggregate_closed=true,
 v=>v.initializer_runtime.new_G2_support=['A_OS'],
 v=>v.initializer_runtime.positive_target_families.pop(),
 v=>v.permitted_runtime_paths.push('src/unrelated.py')]) {
 const bad=structuredClone(value); edit(bad); delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('INITIALIZER_RUNTIME_BROWSER_PASS controls=4');
"""
        browser = subprocess.run([str(managed_node()), '--input-type=module', '-e', code],
                                 cwd=tool / 'phase9-web', input=json.dumps(status), capture_output=True,
                                 text=True, env=tool_environment(), timeout=60)
        self.assertEqual(browser.returncode, 0, browser.stderr)
        self.assertIn('INITIALIZER_RUNTIME_BROWSER_PASS controls=4', browser.stdout)


if __name__ == '__main__':
    unittest.main()
