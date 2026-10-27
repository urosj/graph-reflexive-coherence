import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkedConformance,conformanceLoader} from './tranche8-conformance.js';
const record=JSON.parse(readFileSync(new URL('../../../../../../phase-9-grcv4/tranche-8/P9-8.6-FirstGroup.json',import.meta.url)));
const acceptance=JSON.parse(readFileSync(new URL('../../../../../../phase-9-grcv4/tranche-8/P9-8.6-FirstGroupAcceptance.json',import.meta.url)));
function payload(family='first_group') {return structuredClone({schema:'phase9_tranche8_conformance_v1',checkpoint:'8.6',family,
  decision:family==='first_group'?record:record.families.find(v=>v.family===family),group_record_digest:record.record_digest,
  acceptance,user_accepted:true,first_group_closed:true,aggregate_closed:false,numerical_trajectories_rerun:false});}
test('all five selections are pinned; widening and altered exact domains reject',async()=>{
 for(const family of ['first_group','C_OS','C_CI','A_CI','A_PC']) {
  assert.equal((await checkedConformance(payload(family))).length,family==='first_group'?4:1);
  for(const mutate of [v=>v.user_accepted=false,v=>v.acceptance.decision_digest="changed",v=>v.aggregate_closed=true,v=>v.numerical_trajectories_rerun=true,
   v=>(v.family==='first_group'?v.decision.families[0]:v.decision).exact_domain.mapped_horizon_per_role=10,
   v=>(v.family==='first_group'?v.decision.families[0]:v.decision).limits.arbitrary_graph_numerical_admission=true]) {
    const v=payload(family);mutate(v);await assert.rejects(()=>checkedConformance(v));
  }
 }
});
test('visible selector renders family limits and clears stale or wrong-family results',async()=>{
 const children=[],container={replaceChildren(){children.length=0;},append(x){children.push(x);}};
 const status={textContent:''};let family='first_group',fail=false,wrong=false;
 const load=conformanceLoader(container,status,async()=>({ok:!fail,json:async()=>payload(wrong?'first_group':family)}),()=>({}),()=>family);
 for(family of ['first_group','C_OS','C_CI','A_CI','A_PC']) {
  await load();assert.match(status.textContent,/verified; bounded first-group acceptance recorded/);
  assert(children.some(x=>/No arbitrary-graph/.test(x.textContent)));
  assert.equal(children.filter(x=>x.textContent.startsWith('Limit:')).length,family==='first_group'?4:1);
  assert(children.some(x=>x.href?.includes('checkpoint=8.6')));
 }
 wrong=true;await load();assert.equal(children.length,0);assert.match(status.textContent,/Wrong selected scope/);
 fail=true;await load();assert.equal(children.length,0);assert.match(status.textContent,/Unavailable/);
});
