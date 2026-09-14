"""One real status check; reuse its result across notebook/HTTP/browser transports."""

from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import verify_p977_a_ci_local as audit


class ACISurfaceTests(unittest.TestCase):
    def test_actual_status_and_cached_transport_agreement(self):
        tool = p.ROOT / p.SIDE / 'tool'
        sys.path.insert(0, str(tool / 'src'))
        from grcv4_explorer.phase9_verification import verification_status
        from grcv4_explorer.tooling import managed_node, tool_environment
        status = verification_status(p.ROOT)
        self.assertEqual(status['current_boundary'], 'passed', status.get('error'))
        self.assertEqual(status['a_ci_local_product'], audit.check(initial_review=status['profile_conformance_review']))
        from verify_p977_a_ci_acceptance import check as crossing_check
        self.assertEqual(status['a_ci_crossings'], crossing_check(local_product=status['a_ci_local_product']))
        self.assertEqual(status['a_ci_crossings']['reconciled_crossing_cells'], 7)
        self.assertTrue(status['a_ci_crossings']['user_accepted'])
        self.assertFalse(status['a_ci_crossings']['all_ordered_pairs_verified'])
        self.assertEqual(len(status['accepted_generic_runtime_support']), 2)
        self.assertNotIn(status['a_ci_local_product']['complete_profile_id'], status['accepted_generic_runtime_support'])

        def checked(root):
            self.assertEqual(root, p.ROOT)
            return deepcopy(status)

        # Test orchestration with the already validated result, not three
        # redundant passes through the entire retained predecessor chain.
        book = p.read(tool / 'notebooks/phase9_verification.ipynb')
        cell = next(c for c in book['cells'] if c['id'] == 'query-status')
        namespace = dict(Path=Path, repo_root=p.ROOT, PHASE9_REPO_ROOT=p.ROOT,
            PHASE9_STATUS_ONLY=True, verification_status=checked)
        exec(compile(''.join(cell['source']), 'phase9_verification.ipynb:query-status', 'exec'), namespace)
        self.assertEqual(namespace['phase9_status'], status)
        spec = importlib.util.spec_from_file_location('p977_aci_http', tool / 'scripts/serve_phase9.py')
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        handler.path = '/api/status'
        statuses = []
        handler.send_response = statuses.append
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        handler.wfile = BytesIO()
        with patch.object(server, 'verification_status', side_effect=checked):
            handler.do_GET()
        self.assertEqual(statuses, [200])
        self.assertEqual(json.loads(handler.wfile.getvalue()), status)
        code = """
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {verifiedStatus, canonical} from './verification.js';
const value = JSON.parse(readFileSync(0, 'utf8'));
assert.deepEqual(await verifiedStatus(value), value);
for (const edit of [v=>delete v.a_ci_local_product,
 v=>v.a_ci_local_product.G2_accepted=true,
 v=>v.a_ci_local_product.G3_accepted=true,
 v=>v.a_ci_local_product.user_accepted=true,
 v=>v.a_ci_local_product.aggregate_closed=true,
 v=>v.a_ci_local_product.verified_local_cells=28,
 v=>v.a_ci_local_product.complete_profile_id=v.a_os_local_product.complete_profile_id,
 v=>v.a_ci_local_product.remaining_catalog_cases.pop(),
 v=>v.a_ci_local_product.new_G2_support=['A_CI'],
 v=>v.a_ci_local_product.record_digest='0'.repeat(64),
 v=>delete v.a_ci_crossings,
 v=>v.a_ci_crossings.G2_accepted=true,
 v=>v.a_ci_crossings.all_ordered_pairs_verified=true,
 v=>v.a_ci_crossings.reconciled_crossing_cells=28,
 v=>v.a_ci_crossings.complete_profile_id='A_CI',
 v=>v.a_ci_crossings.record_digest='0'.repeat(64),
 v=>v.a_ci_crossings.user_accepted=false,
 v=>v.a_ci_crossings.acceptance_sha256='0'.repeat(64)]) {
 const bad=structuredClone(value); edit(bad); delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('A_CI_BROWSER_PASS controls=18');
"""
        browser = subprocess.run([str(managed_node()), '--input-type=module', '-e', code],
            cwd=tool / 'phase9-web', input=json.dumps(status), capture_output=True,
            text=True, env=tool_environment(), timeout=30)
        self.assertEqual(browser.returncode, 0, browser.stderr)
        self.assertIn('A_CI_BROWSER_PASS controls=18', browser.stdout)


if __name__ == '__main__':
    unittest.main()
