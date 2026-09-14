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
import verify_p977_c_ci_local as audit


class CCISurfaceTests(unittest.TestCase):
    def test_actual_status_and_cached_transport_agreement(self):
        tool = p.ROOT / p.SIDE / 'tool'
        sys.path.insert(0, str(tool / 'src'))
        from grcv4_explorer.phase9_verification import verification_status
        from grcv4_explorer.tooling import managed_node, tool_environment
        status = verification_status(p.ROOT)
        self.assertEqual(status['current_boundary'], 'passed', status.get('error'))
        self.assertEqual(status['c_ci_local_product'], audit.check(initial_review=status['profile_conformance_review']))
        self.assertEqual(status['c_ci_local_product']['verified_local_cells'], 26)
        self.assertEqual(len(status['c_ci_local_product']['remaining_catalog_cases']), 7)
        self.assertFalse(status['c_ci_local_product']['user_accepted'])
        self.assertFalse(status['c_ci_local_product']['G2_accepted'])
        from verify_p977_c_ci_acceptance import check as crossing_check
        self.assertEqual(status['c_ci_crossings'], crossing_check(local_product=status['c_ci_local_product']))
        self.assertEqual(status['c_ci_crossings']['reconciled_crossing_cells'], 7)
        self.assertEqual(status['c_ci_crossings']['new_execution_cases'], 5)
        self.assertTrue(status['c_ci_crossings']['user_accepted'])
        self.assertFalse(status['c_ci_crossings']['G2_accepted'])
        self.assertEqual(len(status['accepted_generic_runtime_support']), 3)
        self.assertNotIn(status['c_ci_local_product']['complete_profile_id'], status['accepted_generic_runtime_support'])
        self.assertEqual(status['c_ci_g2_review']['catalog_cells'], 33)
        self.assertEqual(status['c_ci_g2_review']['status'], 'pass_proposal_pending_G2_acceptance')
        self.assertFalse(status['c_ci_g2_review']['G2_accepted'])
        self.assertEqual(status['profile_g2'][-1]['state'], 'proposed')
        from profile_g2_registry import checked_reconciliation, registry
        expected=registry(p.ROOT)['reconciliation_views']
        views={key:status[key] for key in expected}
        self.assertEqual(checked_reconciliation(p.ROOT,views),views)
        for key in views:
            bad=deepcopy(views); bad.pop(key)
            with self.assertRaises(ValueError): checked_reconciliation(p.ROOT,bad)
            bad=deepcopy(views); bad[key]['G2_accepted']=True
            with self.assertRaises(ValueError): checked_reconciliation(p.ROOT,bad)
        bad=deepcopy(views);bad['c_ci_crossings']=deepcopy(views['a_ci_crossings'])
        with self.assertRaises(ValueError): checked_reconciliation(p.ROOT,bad)

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
import {verifiedStatus, canonical, renderG2Profiles, renderReconciliation} from './verification.js';
const value = JSON.parse(readFileSync(0, 'utf8'));
assert.deepEqual(await verifiedStatus(value), value);
const element = tag => ({tag, children:[], textContent:'', append(child){this.children.push(child);}, replaceChildren(){this.children=[];}});
const body=element('tbody');
renderG2Profiles(value,body,element);
assert.equal(body.children.length,4);
assert.deepEqual(body.children.map(r=>r.children[2].textContent),['G2 accepted','G2 accepted','G2 accepted','G2 proposal — not accepted']);
assert.equal(body.children[2].children[1].textContent,value.a_ci_g2_review.proposed_additional_support[0]);
renderReconciliation(value,body,element);
assert.equal(body.children.length,6);
const cci=body.children.find(r=>r.children[0].textContent==='c_ci_local_product');
assert.equal(cci.children[1].textContent,'26');
assert.equal(cci.children[2].textContent,'Local evidence pending review');
const crossings=body.children.find(r=>r.children[0].textContent==='c_ci_crossings');
assert.equal(crossings.children[1].textContent,'7');
assert.equal(crossings.children[2].textContent,'Bounded reconciliation accepted');
renderReconciliation({},body,element);
assert.equal(body.children.length,0);
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
 v=>v.profile_g2[2].state='proposed',
 v=>v.profile_g2[0].review.record_digest='0'.repeat(64),
 v=>delete v.a_ci_g2_review,
 v=>v.a_ci_g2_review.G2_accepted=false,
 v=>v.a_ci_g2_review.user_accepted=false,
 v=>v.a_ci_g2_review.G3_accepted=true,
 v=>v.a_ci_g2_review.aggregate_closed=true,
 v=>v.a_ci_g2_review.all_ordered_pairs_verified=true,
 v=>v.a_ci_g2_review.proposed_additional_support=['A_CI'],
 v=>delete v.a_ci_g2_review.obligations['G2-ORDERED-ENDPOINTS'],
 v=>v.a_ci_g2_review.record_digest='0'.repeat(64),
 v=>v.a_ci_g2_review.acceptance_path=v.a_os_g2_review.acceptance_path,
 v=>v.a_ci_g2_review.accepted_support_unchanged.pop(),
 v=>v.a_ci_g2_review.new_G2_support=[],
 v=>v.accepted_generic_runtime_support.push(v.a_ci_g2_review.proposed_additional_support[0]),
 v=>v.profile_g2[1].new_runtime_iterations_authorized=['P9-8.1']]) {
 const bad=structuredClone(value); edit(bad); delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
let count=0;
for(const key of Object.keys(value).filter(k=>k.endsWith('_local_product')||k.endsWith('_crossings'))) {
 for(const edit of [v=>delete v[key],v=>v[key].G2_accepted=true,v=>v[key].record_digest='0'.repeat(64),
                   v=>v[key].complete_profile_id='borrowed',v=>v[key].new_G2_support=['C_CI']]) {
  const bad=structuredClone(value);edit(bad);delete bad.status_digest;
  bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
  await assert.rejects(verifiedStatus(bad)); count++;
 }
}
for(const edit of [v=>v.c_ci_local_product.verified_local_cells=33,
 v=>v.c_ci_local_product.remaining_catalog_cases.pop(),v=>v.c_ci_local_product.user_accepted=true,
 v=>v.c_ci_crossings=structuredClone(v.a_ci_crossings)]) {
 const bad=structuredClone(value);edit(bad);delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));count++;
}
assert.equal(count,34);
for(const edit of [v=>delete v.c_ci_g2_review,v=>v.c_ci_g2_review.G2_accepted=true,
 v=>v.c_ci_g2_review.user_accepted=true,v=>v.c_ci_g2_review.catalog_cells=28,
 v=>v.c_ci_g2_review.all_ordered_pairs_verified=true,v=>v.c_ci_g2_review.record_digest='0'.repeat(64),
 v=>v.c_ci_g2_review.proposed_additional_support=['C_CI'],v=>v.c_ci_g2_review.accepted_support_unchanged=[],
 v=>v.profile_g2[3].state='accepted',v=>v.accepted_generic_runtime_support.push(v.c_ci_g2_review.proposed_additional_support[0])]) {
 const bad=structuredClone(value);edit(bad);delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('C_CI_BROWSER_PASS controls=80');
"""
        browser = subprocess.run([str(managed_node()), '--input-type=module', '-e', code],
            cwd=tool / 'phase9-web', input=json.dumps(status), capture_output=True,
            text=True, env=tool_environment(), timeout=30)
        self.assertEqual(browser.returncode, 0, browser.stderr)
        self.assertIn('C_CI_BROWSER_PASS controls=80', browser.stdout)


if __name__ == '__main__':
    unittest.main()
