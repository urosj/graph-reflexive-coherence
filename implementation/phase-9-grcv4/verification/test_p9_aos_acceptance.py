"""Acceptance binding, retained executions and accepted API/browser/notebook."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import p9_aos_acceptance as a
import test_p9_aos_review as previous

ROOT=a.review.b.ROOT
TOOL=ROOT/a.SIDE
sys.path.insert(0,str(TOOL/'src'))
from grcv4_explorer import aos


class AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=a.review.checked(ROOT)
        cls.status=aos.aos_status(ROOT)

    def test_bounded_acceptance_preserves_original_execution(self):
        decision=a.decision(ROOT)
        self.assertTrue(decision['user_accepted'])
        self.assertFalse(self.record['user_accepted'])
        self.assertEqual((ROOT/a.review.PATH).read_bytes(),a.original(ROOT,a.review.PATH))
        self.assertTrue(all(r['user_accepted'] and r['state']=='bounded_accepted' for r in self.status['checkpoints']))
        matrix=next(r['execution'] for r in self.status['checkpoints'] if r['checkpoint']=='9.3')
        self.assertEqual(matrix['counts'],dict(bounded_accepted=20,passed_pending_acceptance=0,unselected_not_executed=20))
        self.assertEqual(matrix['execution_counts']['passed_pending_acceptance'],4)
        self.assertFalse(decision['aggregate_closed'])
        self.assertFalse(decision['full_GRC9V4_conformance'])
        self.assertTrue(decision['original_large_reset_excluded'])
        for ref in decision['validation']:
            self.assertEqual((ROOT/ref['path']).read_bytes(),a.original(ROOT,ref['path']))

    def test_resealed_decision_and_live_source_mutations_reject(self):
        decision=a.decision(ROOT);read=Path.read_bytes
        for field,new in [('aggregate_closed',True),('user_accepted',False),('original_large_reset_excluded',False)]:
            bad=deepcopy(decision);bad[field]=new
            raw=json.dumps(a.review.b.seal(bad)).encode()
            with patch.object(Path,'read_bytes',lambda p:raw if p==ROOT/a.PATH else read(p)):
                with self.assertRaises(ValueError):a.decision(ROOT)
        for name in a.CHANGED:
            target=ROOT/name
            with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
                with self.assertRaises(ValueError):a.decision(ROOT)
        self.assertIsNone(a.previous_sha(ROOT,'unregistered.py','0'*64))

    def test_source_index_and_http_notebook(self):
        previous.AOSReviewTests.test_source_drift_and_index_boundary(self)
        previous.AOSReviewTests.test_http_and_real_notebook_cell(self)
        raw,ref=aos.aos_source(ROOT,a.PATH)
        self.assertEqual(a.review.b.sha(raw),ref['sha256'])
        self.assertTrue(json.loads(raw)['user_accepted'])

    def test_browser_acceptance_pending_and_failed_refresh(self):
        with patch.object(a,'decision',return_value=None):pending=aos.aos_status(ROOT)
        script="""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {accepted,pending}=JSON.parse(readFileSync(0,'utf8'));
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let listener,ok=true;
function element(tag){return {tag,children:[],append(e){this.children.push(e)},insertCell(){const e=element('td');this.append(e);return e},insertRow(){const e=element('tr');this.append(e);return e},createTHead(){const e=element('thead');this.append(e);return e},createTBody(){const e=element('tbody');this.append(e);return e}};}
globalThis.document={getElementById(id){return id==='aos-refresh'?{addEventListener(_,fn){listener=fn}}:id==='aos-status'?status:output},createElement:element};
globalThis.fetch=async()=>({ok,json:async()=>accepted});
const {aosRows}=await import('./aos.js');
assert.equal(aosRows(accepted).filter(r=>r.accepted).length,16);
assert.equal(aosRows(pending).filter(r=>r.accepted).length,0);
assert.throws(()=>aosRows({...pending,user_accepted:true}));
assert.throws(()=>aosRows({...accepted,aggregate_closed:true}));
assert.throws(()=>aosRows({...accepted,acceptance_digest:'0'.repeat(64)}));
await listener();assert.equal(output.children[0].tag,'table');assert.match(status.textContent,/accepted/);
ok=false;await listener();assert.equal(output.children.length,0);assert.match(status.textContent,/failed/);
"""
        result=subprocess.run([str(previous.managed_node()),'--input-type=module','-e',script],
            input=json.dumps(dict(accepted=self.status,pending=pending)),text=True,capture_output=True,
            cwd=TOOL/'phase9-web',timeout=30,env=previous.tool_environment())
        self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':unittest.main()
