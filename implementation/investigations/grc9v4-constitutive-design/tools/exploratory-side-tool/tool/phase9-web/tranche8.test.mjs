import {test} from 'node:test';
import assert from 'node:assert/strict';
import {TRANCHE8_EVIDENCE as evidence} from './tranche8-evidence.js';
import {checkedTranche8, renderTranche8, sourceURL, tranche8Loader} from './tranche8.js';

const element = tag => ({tag, textContent:'', children:[], append(...nodes){this.children.push(...nodes);}, replaceChildren(...nodes){this.children=nodes;}});
const text = node => node.textContent + node.children.map(text).join(' ');

test('all ten accepted 8.3 profiles and partial 8.4 coverage actually render', () => {
  const out=element('div'); renderTranche8(evidence,out,element);
  const content=text(out);
  for(const row of evidence.profiles) assert.ok(content.includes(row.family));
  for(const s of ['64/322','258 pending','INCOMPLETE CASE','event committed=true','No native trajectory rerun','not runtime acceptance']) assert.ok(content.includes(s),s);
  assert.ok(out.children.length > 20);
});

test('mutated counts, scope, input identities and failures cannot be promoted', () => {
  for(const mutate of [v=>v.coverage.accepted_cells=322, v=>v.coverage.aggregate_closed=true,
    v=>v.profiles.pop(),v=>v.configuration.families[0].runtime_accepted=true,
    v=>v.coverage.runs[0].cases.find(r=>!r.case_passed).case_passed=true,
    v=>v.verification.native_trajectories_rerun=true,v=>v.source_refs[0].sha256='0'.repeat(64),
    v=>v.dependency_ready_snapshot.push('P9-8.5')]) {
    const value=structuredClone(evidence);mutate(value);assert.throws(()=>checkedTranche8(value));
  }
});

test('only exact indexed source links are exposed', () => {
  const ref=evidence.source_refs[0];assert.ok(sourceURL(ref).startsWith('/api/tranche8/source?path='));
  assert.throws(()=>sourceURL({...ref,path:'../../secret'}));
  assert.throws(()=>sourceURL({...ref,sha256:'0'.repeat(64)}));
});

test('failed refresh clears previous success and ignores delayed old response', async () => {
  const out=element('div'), status=element('p');let fail=false;
  const load=tranche8Loader(out,status,async()=>({ok:!fail,json:async()=>evidence}),element);
  await load();assert.ok(out.children.length);fail=true;await load();assert.equal(out.children.length,0);
  assert.match(status.textContent,/Unavailable/);
  let resolve;let n=0;
  const reload=tranche8Loader(out,status,async()=>++n===1 ? new Promise(r=>resolve=r) : {ok:false},element);
  const first=reload();await reload();resolve({ok:true,json:async()=>evidence});await first;
  assert.equal(out.children.length,0);assert.match(status.textContent,/Unavailable/);
});
