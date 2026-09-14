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
        from profile_g2_registry import registry, view
        from verify_p977_a_ci_g2 import RECORD
        self.assertEqual(status['profile_g2'], [view(r) for r in registry(p.ROOT)['records']])
        self.assertEqual(status['a_ci_g2_review']['record_digest'], p.read(p.ROOT/RECORD)['record_digest'])
        self.assertEqual(status['a_ci_g2_review']['status'], 'pass_proposal_pending_G2_acceptance')
        self.assertFalse(status['a_ci_g2_review']['G2_accepted'])

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
        handler.path = '/g2-registry.js'
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(statuses, [200, 200])
        self.assertEqual(handler.wfile.getvalue(), (tool/'phase9-web/g2-registry.js').read_bytes())
        code = """
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {verifiedStatus, canonical, renderG2Profiles} from './verification.js';
const value = JSON.parse(readFileSync(0, 'utf8'));
assert.deepEqual(await verifiedStatus(value), value);
const element = tag => ({tag, children:[], textContent:'', append(child){this.children.push(child);}, replaceChildren(){this.children=[];}});
const body=element('tbody');
renderG2Profiles(value,body,element);
assert.equal(body.children.length,3);
assert.deepEqual(body.children.map(r=>r.children[2].textContent),['G2 accepted','G2 accepted','G2 proposal — not accepted']);
assert.equal(body.children[2].children[1].textContent,value.a_ci_g2_review.proposed_additional_support[0]);
renderG2Profiles({},body,element);
assert.equal(body.children.length,0);
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
 v=>v.a_ci_crossings.acceptance_sha256='0'.repeat(64),
 v=>delete v.profile_g2,
 v=>v.profile_g2.push(structuredClone(v.profile_g2[0])),
 v=>v.profile_g2[2].state='accepted',
 v=>v.profile_g2[0].review.record_digest='0'.repeat(64),
 v=>delete v.a_ci_g2_review,
 v=>v.a_ci_g2_review.G2_accepted=true,
 v=>v.a_ci_g2_review.user_accepted=true,
 v=>v.a_ci_g2_review.G3_accepted=true,
 v=>v.a_ci_g2_review.aggregate_closed=true,
 v=>v.a_ci_g2_review.all_ordered_pairs_verified=true,
 v=>v.a_ci_g2_review.proposed_additional_support=['A_CI'],
 v=>delete v.a_ci_g2_review.obligations['G2-ORDERED-ENDPOINTS'],
 v=>v.a_ci_g2_review.record_digest='0'.repeat(64),
 v=>v.a_ci_g2_review.acceptance_path=v.a_os_g2_review.acceptance_path,
 v=>v.a_ci_g2_review.accepted_support_unchanged.pop(),
 v=>v.a_ci_g2_review.new_G2_support=v.a_ci_g2_review.proposed_additional_support,
 v=>v.accepted_generic_runtime_support.push(v.a_ci_g2_review.proposed_additional_support[0]),
 v=>v.profile_g2[1].new_runtime_iterations_authorized=['P9-8.1']]) {
 const bad=structuredClone(value); edit(bad); delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('A_CI_BROWSER_PASS controls=36');
"""
        browser = subprocess.run([str(managed_node()), '--input-type=module', '-e', code],
            cwd=tool / 'phase9-web', input=json.dumps(status), capture_output=True,
            text=True, env=tool_environment(), timeout=30)
        self.assertEqual(browser.returncode, 0, browser.stderr)
        self.assertIn('A_CI_BROWSER_PASS controls=36', browser.stdout)


if __name__ == '__main__':
    unittest.main()
