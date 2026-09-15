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
        self.assertEqual(len(status['accepted_generic_runtime_support']), 8)
        self.assertIn(status['c_ci_local_product']['complete_profile_id'], status['accepted_generic_runtime_support'])
        self.assertEqual(status['c_ci_g2_review']['catalog_cells'], 33)
        self.assertEqual(status['c_ci_g2_review']['status'], 'accepted')
        self.assertTrue(status['c_ci_g2_review']['G2_accepted'])
        self.assertEqual(status['profile_g2'][3]['state'], 'accepted')
        self.assertEqual(status['profile_g2'][4]['profile_family_id'],'A_PC')
        self.assertEqual(status['profile_g2'][4]['state'],'accepted')
        self.assertEqual(status['profile_g2'][5]['profile_family_id'],'C_PC')
        self.assertEqual(status['profile_g2'][5]['state'],'accepted')
        self.assertEqual(status['profile_g2'][6]['profile_family_id'],'A_CI_PC')
        self.assertEqual(status['profile_g2'][6]['state'],'accepted')
        self.assertEqual(status['profile_g2'][-1]['profile_family_id'],'C_CI_PC')
        self.assertEqual(status['profile_g2'][-1]['state'],'accepted')
        proposal=status['a_pc_g2_review']
        self.assertEqual(proposal['status'],'accepted')
        self.assertEqual(proposal['catalog_cells'],28)
        self.assertTrue(proposal['G2_accepted'])
        self.assertTrue(proposal['user_accepted'])
        self.assertEqual(proposal['new_G2_support'],proposal['proposed_additional_support'])
        self.assertEqual(proposal['accepted_support_unchanged'],sorted(r['complete_profile_id'] for r in status['profile_g2'][:4]))
        from profile_g2_registry import checked_reconciliation, registry
        expected=registry(p.ROOT)['reconciliation_views']
        from verify_p977_c_ci_pc_local import check as c_coupled_check
        c_coupled=status['c_ci_pc_local_product']
        self.assertEqual(c_coupled,c_coupled_check(initial_review=status['profile_conformance_review']))
        self.assertEqual((c_coupled['test_count'],c_coupled['verified_local_cells']),(5,26))
        self.assertEqual(len(c_coupled['remaining_catalog_cases']),7)
        for flag in ('user_accepted','G2_accepted','G3_accepted','aggregate_closed'):
            self.assertFalse(c_coupled[flag])
        self.assertEqual(c_coupled['new_G2_support'],[])
        self.assertIn(c_coupled['complete_profile_id'],status['accepted_generic_runtime_support'])
        from verify_p977_c_ci_pc_acceptance import check as c_coupled_crossing_check
        c_coupled_crossings=status['c_ci_pc_crossings']
        self.assertEqual(c_coupled_crossings,c_coupled_crossing_check(local_product=c_coupled))
        self.assertEqual((c_coupled_crossings['test_count'],c_coupled_crossings['new_execution_cases'],c_coupled_crossings['retained_alias_count']),(4,8,3))
        self.assertEqual((c_coupled_crossings['local_cells'],c_coupled_crossings['reconciled_crossing_cells']),(26,7))
        self.assertEqual(c_coupled_crossings['complete_profile_id'],c_coupled['complete_profile_id'])
        self.assertTrue(c_coupled_crossings['user_accepted'])
        for flag in ('G2_accepted','G3_accepted','aggregate_closed','all_ordered_pairs_verified'):
            self.assertFalse(c_coupled_crossings[flag])
        self.assertEqual(c_coupled_crossings['new_G2_support'],[])
        self.assertIn('Exact accepted G2 declarations (8)',status['next_gate'])
        self.assertNotIn('C_CI_PC: 26 local cells',status['next_gate'])
        c_coupled_gate=status['c_ci_pc_g2_review']
        self.assertEqual(c_coupled_gate['status'],'accepted')
        self.assertEqual(c_coupled_gate['catalog_cells'],33)
        self.assertEqual(c_coupled_gate['proposed_additional_support'],[c_coupled['complete_profile_id']])
        self.assertEqual(c_coupled_gate['accepted_support_unchanged'],sorted(set(status['accepted_generic_runtime_support'])-{c_coupled['complete_profile_id']}))
        self.assertTrue(c_coupled_gate['user_accepted'])
        self.assertTrue(c_coupled_gate['G2_accepted'])
        for flag in ('G3_accepted','aggregate_closed','all_ordered_pairs_verified'):
            self.assertFalse(c_coupled_gate[flag])
        self.assertEqual(c_coupled_gate['new_G2_support'],c_coupled_gate['proposed_additional_support'])
        self.assertEqual(c_coupled_gate['supplemental_interface_methods'],1)
        self.assertEqual(c_coupled_gate['numerical_tests_rerun'],0)
        views={key:status[key] for key in expected}
        self.assertEqual(checked_reconciliation(p.ROOT,views),views)
        self.assertEqual(status['a_pc_local_product']['verified_local_cells'],21)
        from verify_p977_a_ci_pc_local import check as coupled_check
        coupled=status['a_ci_pc_local_product']
        self.assertEqual(coupled,coupled_check(initial_review=status['profile_conformance_review']))
        self.assertEqual((coupled['test_count'],coupled['verified_local_cells']),(5,21))
        self.assertEqual(len(coupled['remaining_catalog_cases']),7)
        for flag in ('user_accepted','G2_accepted','G3_accepted','aggregate_closed'):
            self.assertFalse(coupled[flag])
        self.assertEqual(coupled['new_G2_support'],[])
        self.assertIn(coupled['complete_profile_id'],status['accepted_generic_runtime_support'])
        from verify_p977_a_ci_pc_acceptance import check as coupled_crossing_check
        coupled_crossings=status['a_ci_pc_crossings']
        self.assertEqual(coupled_crossings,coupled_crossing_check(local_product=coupled))
        self.assertEqual((coupled_crossings['test_count'],coupled_crossings['new_execution_cases'],coupled_crossings['retained_alias_count']),(4,7,5))
        self.assertEqual((coupled_crossings['local_cells'],coupled_crossings['reconciled_crossing_cells']),(21,7))
        self.assertEqual(coupled_crossings['complete_profile_id'],coupled['complete_profile_id'])
        self.assertTrue(coupled_crossings['user_accepted'])
        for flag in ('G2_accepted','G3_accepted','aggregate_closed','all_ordered_pairs_verified'):
            self.assertFalse(coupled_crossings[flag])
        self.assertEqual(coupled_crossings['new_G2_support'],[])
        coupled_gate=status['a_ci_pc_g2_review']
        self.assertEqual(coupled_gate['status'],'accepted')
        self.assertEqual(coupled_gate['catalog_cells'],28)
        self.assertEqual(coupled_gate['proposed_additional_support'],[coupled['complete_profile_id']])
        self.assertEqual(coupled_gate['accepted_support_unchanged'],sorted(r['complete_profile_id'] for r in status['profile_g2'][:6]))
        for flag in ('user_accepted','G2_accepted'):
            self.assertTrue(coupled_gate[flag])
        for flag in ('G3_accepted','aggregate_closed','all_ordered_pairs_verified'):
            self.assertFalse(coupled_gate[flag])
        self.assertEqual(coupled_gate['new_G2_support'],coupled_gate['proposed_additional_support'])
        cpc=status['c_pc_local_product']
        self.assertEqual((cpc['test_count'],cpc['verified_local_cells']),(5,26))
        self.assertEqual(len(cpc['remaining_catalog_cases']),7)
        self.assertFalse(cpc['user_accepted'])
        self.assertFalse(cpc['G2_accepted'])
        self.assertFalse(cpc['aggregate_closed'])
        self.assertFalse(cpc['G3_accepted'])
        self.assertEqual(cpc['new_G2_support'],[])
        self.assertIn(cpc['complete_profile_id'],status['accepted_generic_runtime_support'])
        cpc_crossings=status['c_pc_crossings']
        self.assertEqual((cpc_crossings['test_count'],cpc_crossings['new_execution_cases'],cpc_crossings['retained_alias_count']),(3,4,7))
        self.assertEqual((cpc_crossings['local_cells'],cpc_crossings['reconciled_crossing_cells']),(26,7))
        self.assertEqual(cpc_crossings['complete_profile_id'],cpc['complete_profile_id'])
        self.assertTrue(cpc_crossings['user_accepted'])
        self.assertFalse(cpc_crossings['G2_accepted'])
        self.assertFalse(cpc_crossings['all_ordered_pairs_verified'])
        cpc_gate=status['c_pc_g2_review']
        self.assertEqual(cpc_gate['status'],'accepted')
        self.assertEqual(cpc_gate['catalog_cells'],33)
        self.assertEqual(cpc_gate['proposed_additional_support'],[cpc['complete_profile_id']])
        self.assertEqual(cpc_gate['accepted_support_unchanged'],sorted(r['complete_profile_id'] for r in status['profile_g2'][:5]))
        self.assertTrue(cpc_gate['G2_accepted'])
        self.assertTrue(cpc_gate['user_accepted'])
        self.assertEqual(cpc_gate['new_G2_support'],[cpc['complete_profile_id']])
        apc=status['a_pc_crossings']
        self.assertEqual((apc['reconciled_crossing_cells'],apc['new_execution_cases'],apc['retained_alias_count']),(7,5,7))
        self.assertTrue(apc['user_accepted'])
        self.assertFalse(apc['G2_accepted'])
        self.assertFalse(apc['all_ordered_pairs_verified'])
        self.assertIn(apc['complete_profile_id'],status['accepted_generic_runtime_support'])
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
assert.equal(body.children.length,8);
assert.deepEqual(body.children.map(r=>r.children[2].textContent),['G2 accepted','G2 accepted','G2 accepted','G2 accepted','G2 accepted','G2 accepted','G2 accepted','G2 accepted']);
assert.equal(body.children[7].children[1].textContent,value.c_ci_pc_g2_review.proposed_additional_support[0]);
assert.equal(body.children[6].children[1].textContent,value.a_ci_pc_g2_review.proposed_additional_support[0]);
assert.equal(body.children[5].children[1].textContent,value.c_pc_g2_review.proposed_additional_support[0]);
assert.equal(body.children[4].children[1].textContent,value.a_pc_g2_review.proposed_additional_support[0]);
assert.equal(body.children[2].children[1].textContent,value.a_ci_g2_review.proposed_additional_support[0]);
renderReconciliation(value,body,element);
assert.equal(body.children.length,Object.keys(value).filter(k=>k.endsWith('_local_product')||k.endsWith('_crossings')).length);
const cci=body.children.find(r=>r.children[0].textContent==='c_ci_local_product');
const cCoupled=body.children.find(r=>r.children[0].textContent==='c_ci_pc_local_product');
assert.ok(cCoupled);
assert.equal(cCoupled.children[1].textContent,'26');
assert.equal(cCoupled.children[2].textContent,'Local evidence pending review');
const cCoupledCrossings=body.children.find(r=>r.children[0].textContent==='c_ci_pc_crossings');
assert.ok(cCoupledCrossings);
assert.equal(cCoupledCrossings.children[1].textContent,'7');
assert.equal(cCoupledCrossings.children[2].textContent,'Bounded reconciliation accepted');
const coupled=body.children.find(r=>r.children[0].textContent==='a_ci_pc_local_product');
assert.ok(coupled);
assert.equal(coupled.children[2].textContent,'Local evidence pending review');
const coupledCrossings=body.children.find(r=>r.children[0].textContent==='a_ci_pc_crossings');
assert.ok(coupledCrossings);
assert.equal(coupledCrossings.children[1].textContent,'7');
assert.equal(coupledCrossings.children[2].textContent,'Bounded reconciliation accepted');
const cpc=body.children.find(r=>r.children[0].textContent==='c_pc_local_product');
assert.equal(cpc.children[1].textContent,'26');
assert.equal(cpc.children[2].textContent,'Local evidence pending review');
const cpcCrossings=body.children.find(r=>r.children[0].textContent==='c_pc_crossings');
assert.equal(cpcCrossings.children[1].textContent,'7');
assert.equal(cpcCrossings.children[2].textContent,'Bounded reconciliation accepted');
assert.equal(cci.children[1].textContent,'26');
assert.equal(cci.children[2].textContent,'Local evidence pending review');
const crossings=body.children.find(r=>r.children[0].textContent==='c_ci_crossings');
assert.equal(crossings.children[1].textContent,'7');
assert.equal(crossings.children[2].textContent,'Bounded reconciliation accepted');
const apc=body.children.find(r=>r.children[0].textContent==='a_pc_crossings');
assert.equal(apc.children[1].textContent,'7');
assert.equal(apc.children[2].textContent,'Bounded reconciliation accepted');
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
assert.equal(count,5*Object.keys(value).filter(k=>k.endsWith('_local_product')||k.endsWith('_crossings')).length+4);
for(const edit of [v=>delete v.c_ci_g2_review,v=>v.c_ci_g2_review.G2_accepted=false,
 v=>v.c_ci_g2_review.user_accepted=false,v=>v.c_ci_g2_review.catalog_cells=28,
 v=>v.c_ci_g2_review.all_ordered_pairs_verified=true,v=>v.c_ci_g2_review.record_digest='0'.repeat(64),
 v=>v.c_ci_g2_review.proposed_additional_support=['C_CI'],v=>v.c_ci_g2_review.accepted_support_unchanged=[],
 v=>v.profile_g2[3].state='proposed',v=>v.accepted_generic_runtime_support.push(v.c_ci_g2_review.proposed_additional_support[0])]) {
 const bad=structuredClone(value);edit(bad);delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('C_CI_BROWSER_PASS registered reconciliation controls='+count);
for(const edit of [v=>delete v.a_pc_g2_review,v=>v.a_pc_g2_review.G2_accepted=false,
 v=>v.a_pc_g2_review.user_accepted=false,v=>v.a_pc_g2_review.catalog_cells=27,
 v=>v.a_pc_g2_review.all_ordered_pairs_verified=true,v=>v.a_pc_g2_review.record_digest='0'.repeat(64),
 v=>v.a_pc_g2_review.proposed_additional_support=['A_PC'],v=>v.a_pc_g2_review.accepted_support_unchanged=[],
 v=>v.profile_g2[4].state='proposed',v=>v.accepted_generic_runtime_support.push(v.a_pc_g2_review.proposed_additional_support[0])]) {
 const bad=structuredClone(value);edit(bad);delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('A_PC_G2_ACCEPTANCE_BROWSER_PASS');
for(const edit of [v=>delete v.c_pc_g2_review,v=>v.c_pc_g2_review.G2_accepted=false,
 v=>v.c_pc_g2_review.user_accepted=false,v=>v.c_pc_g2_review.catalog_cells=28,
 v=>v.c_pc_g2_review.all_ordered_pairs_verified=true,v=>v.c_pc_g2_review.record_digest='0'.repeat(64),
 v=>v.c_pc_g2_review.proposed_additional_support=['C_PC'],v=>v.c_pc_g2_review.accepted_support_unchanged=[],
 v=>v.profile_g2[5].state='proposed',v=>v.accepted_generic_runtime_support.push(v.c_pc_g2_review.proposed_additional_support[0])]) {
 const bad=structuredClone(value);edit(bad);delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('C_PC_G2_ACCEPTANCE_BROWSER_PASS');
for(const edit of [v=>delete v.a_ci_pc_g2_review,v=>v.a_ci_pc_g2_review.G2_accepted=false,
 v=>v.a_ci_pc_g2_review.user_accepted=false,v=>v.a_ci_pc_g2_review.catalog_cells=33,
 v=>v.a_ci_pc_g2_review.all_ordered_pairs_verified=true,v=>v.a_ci_pc_g2_review.record_digest='0'.repeat(64),
 v=>v.a_ci_pc_g2_review.proposed_additional_support=['A_CI_PC'],v=>v.a_ci_pc_g2_review.accepted_support_unchanged=[],
 v=>v.profile_g2[6].state='proposed',v=>v.accepted_generic_runtime_support.push(v.a_ci_pc_g2_review.proposed_additional_support[0])]) {
 const bad=structuredClone(value);edit(bad);delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('A_CI_PC_G2_ACCEPTANCE_BROWSER_PASS');
for(const edit of [v=>v.c_ci_pc_local_product.verified_local_cells=33,
 v=>v.c_ci_pc_local_product.remaining_catalog_cases.pop(),
 v=>v.c_ci_pc_local_product.user_accepted=true,v=>v.c_ci_pc_local_product.G3_accepted=true]) {
 const bad=structuredClone(value);edit(bad);delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('C_CI_PC_LOCAL_BROWSER_PASS');
for(const edit of [v=>v.c_ci_pc_crossings.user_accepted=false,
 v=>v.c_ci_pc_crossings.G3_accepted=true,v=>v.c_ci_pc_crossings.aggregate_closed=true,
 v=>v.c_ci_pc_crossings.all_ordered_pairs_verified=true,
 v=>v.c_ci_pc_crossings.reconciled_crossing_cells=33,
 v=>v.c_ci_pc_crossings.new_execution_cases=7,
 v=>v.c_ci_pc_crossings.retained_alias_count=7,
 v=>v.c_ci_pc_crossings=structuredClone(v.a_ci_pc_crossings)]) {
 const bad=structuredClone(value);edit(bad);delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('C_CI_PC_CROSSINGS_BROWSER_PASS');
for(const edit of [v=>delete v.c_ci_pc_g2_review,v=>v.c_ci_pc_g2_review.G2_accepted=false,
 v=>v.c_ci_pc_g2_review.user_accepted=false,v=>v.c_ci_pc_g2_review.catalog_cells=28,
 v=>v.c_ci_pc_g2_review.all_ordered_pairs_verified=true,v=>v.c_ci_pc_g2_review.record_digest='0'.repeat(64),
 v=>v.c_ci_pc_g2_review.proposed_additional_support=['C_CI_PC'],v=>v.c_ci_pc_g2_review.accepted_support_unchanged=[],
 v=>v.profile_g2[7].state='proposed',v=>v.accepted_generic_runtime_support.push(v.c_ci_pc_g2_review.proposed_additional_support[0])]) {
 const bad=structuredClone(value);edit(bad);delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
console.log('C_CI_PC_G2_ACCEPTANCE_BROWSER_PASS');
"""
        browser = subprocess.run([str(managed_node()), '--input-type=module', '-e', code],
            cwd=tool / 'phase9-web', input=json.dumps(status), capture_output=True,
            text=True, env=tool_environment(), timeout=30)
        self.assertEqual(browser.returncode, 0, browser.stderr)
        self.assertIn('C_CI_BROWSER_PASS registered reconciliation controls=', browser.stdout)
        self.assertIn('A_PC_G2_ACCEPTANCE_BROWSER_PASS',browser.stdout)
        self.assertIn('C_PC_G2_ACCEPTANCE_BROWSER_PASS',browser.stdout)
        self.assertIn('A_CI_PC_G2_ACCEPTANCE_BROWSER_PASS',browser.stdout)
        self.assertIn('C_CI_PC_LOCAL_BROWSER_PASS',browser.stdout)
        self.assertIn('C_CI_PC_CROSSINGS_BROWSER_PASS',browser.stdout)
        self.assertIn('C_CI_PC_G2_ACCEPTANCE_BROWSER_PASS',browser.stdout)


if __name__ == '__main__':
    unittest.main()
