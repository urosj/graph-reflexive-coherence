import {test} from 'node:test';
import assert from 'node:assert/strict';
import {checkedTranche9,lifecycleLoader} from './tranche9.js';
const families=['C_OS','C_CI','A_CI','A_PC'];
const payload={schema:'phase9_tranche9_first_group_v1',iteration:'P9-9.1b',families,
  user_accepted:true,aggregate_closed:false,full_GRC9V4_conformance:false,
  check_level:'retained_integrity_only_no_numerical_rerun',state:'bounded_accepted',
  optional_completion:'unselected',disabled_compatibility:'pending_16_selected_cells',
  records:families.map(family=>({family,tests:6,outcome:'passed',exact_replay:true,elapsed_seconds:1})),
  source_refs:[{path:'implementation/phase-9-grcv4/tranche-9/P9-9.1b-Review.md'}]};
test('four families and bounded acceptance are never inferred from widened responses',()=>{
  assert.equal(checkedTranche9(payload),payload);
  for(const key of ['aggregate_closed','full_GRC9V4_conformance'])
    assert.throws(()=>checkedTranche9({...payload,[key]:true}));
  assert.throws(()=>checkedTranche9({...payload,families:[...families,'A_OS']}));
  assert.throws(()=>checkedTranche9({...payload,records:payload.records.slice(1)}));
});
test('actual loader shows results and clears stale evidence on failure',async()=>{
  const children=[],container={replaceChildren(){children.length=0;},append(x){children.push(x);}};
  const status={textContent:''};let value=structuredClone(payload),ok=true;
  const load=lifecycleLoader(container,status,async()=>({ok,json:async()=>value}),()=>({}));
  await load();assert.match(status.textContent,/bounded acceptance recorded/);
  assert.equal(children.filter(x=>/6 tests passed/.test(x.textContent)).length,4);
  assert(children.some(x=>x.href?.startsWith('/api/tranche9/source?')));
  value.records[0].outcome='failed';await load();assert.equal(children.length,0);
  assert.match(status.textContent,/Unexpected/);
  ok=false;await load();assert.equal(children.length,0);assert.match(status.textContent,/Unavailable/);
});

import {checkedCompatibility,compatibilityLoader} from './tranche9.js';
const compatibility={matrix_reconciliation:{iteration:'P9-9.3',outcome:'passed',user_accepted:true,native_execution:false,record_digest:'b'.repeat(64)},schema:'p992-compatibility-status-v1',families,selected_cells:16,passed_cells:16,unselected_cells:24,
 user_accepted:true,aggregate_closed:false,full_GRC9V4_conformance:false,crossings_executed:false,
 check_level:'retained_integrity_only_no_native_rerun',source_refs:[{path:'implementation/phase-9-grcv4/tranche-9/P9-9.2-Review.md'}],
 cells:['A','C'].flatMap(c=>['OS','CI','PC','CI_PC','RG2b'].flatMap(r=>['transition','state','observable','lifecycle'].map(surface=>{
 const family=c+'_'+r;return {family,surface,iteration_id:`P9-9.2-${family}-${surface}`,
 state:families.includes(family)?'bounded_accepted':'unselected',record_digest:families.includes(family)?'a'.repeat(64):null};})))};
test('exact forty-cell matrix rejects missing, duplicate and promoted cells',()=>{
 assert.equal(checkedCompatibility(compatibility),compatibility);
 assert.throws(()=>checkedCompatibility({...compatibility,matrix_reconciliation:null}));
 assert.throws(()=>checkedCompatibility({...compatibility,matrix_reconciliation:{...compatibility.matrix_reconciliation,user_accepted:false}}));
 for(const key of ['native_execution'])assert.throws(()=>checkedCompatibility({...compatibility,matrix_reconciliation:{...compatibility.matrix_reconciliation,[key]:true}}));
 assert.throws(()=>checkedCompatibility({...compatibility,user_accepted:false}));
 for(const key of ['aggregate_closed','full_GRC9V4_conformance','crossings_executed'])assert.throws(()=>checkedCompatibility({...compatibility,[key]:true}));
 assert.throws(()=>checkedCompatibility({...compatibility,cells:compatibility.cells.slice(1)}));
 const duplicate=structuredClone(compatibility);duplicate.cells[1]=duplicate.cells[0];assert.throws(()=>checkedCompatibility(duplicate));
 const widened=structuredClone(compatibility);widened.cells[0].state='executed_pending_acceptance';assert.throws(()=>checkedCompatibility(widened));
});
test('compatibility loader renders all cells and clears stale data',async()=>{
 const create=()=>({children:[],append(x){this.children.push(x);}}),container=create();container.replaceChildren=()=>{container.children=[];};
 const status={textContent:''};let value=structuredClone(compatibility),ok=true;
 const load=compatibilityLoader(container,status,async()=>({ok,json:async()=>value}),create);
 await load();assert.match(status.textContent,/bounded acceptance recorded/);
 assert.equal(container.children[2].children.length,41);
 assert(container.children.some(x=>x.href?.startsWith('/api/tranche9/compatibility/source?')));
 value.crossings_executed=true;await load();assert.equal(container.children.length,0);
 ok=false;await load();assert.equal(container.children.length,0);
});

import {checkedCrossings,crossingsLoader} from './tranche9.js';
const crossings={schema:'p994a-crossing-status-v1',iteration:'P9-9.4a',families,
  user_accepted:true,public_api:false,aggregate_closed:false,full_GRC9V4_conformance:false,
  state:'bounded_accepted',check_level:'retained_integrity_only_no_native_rerun',
  records:families.map(family=>({family,tests:4,outcome:'passed',record_digest:'a'.repeat(64)})),
  source_refs:[{path:'implementation/phase-9-grcv4/tranche-9/P9-9.4a-Review.md'}]};
test('crossing scope refuses public API/acceptance promotion or a missing family',()=>{
  assert.equal(checkedCrossings(crossings),crossings);
  for(const key of ['public_api','aggregate_closed','full_GRC9V4_conformance'])
    assert.throws(()=>checkedCrossings({...crossings,[key]:true}));
  assert.throws(()=>checkedCrossings({...crossings,records:crossings.records.slice(1)}));
});
test('crossing loader renders all families, linked evidence, and clears on failure',async()=>{
  const children=[],container={replaceChildren(){children.length=0;},append(x){children.push(x);}};
  const status={textContent:''};let ok=true;
  const load=crossingsLoader(container,status,async()=>({ok,json:async()=>crossings}),()=>({}));
  await load();assert.match(status.textContent,/bounded acceptance recorded/);
  assert.equal(children.filter(x=>/4 tests passed/.test(x.textContent)).length,4);
  assert(children.some(x=>x.href?.startsWith('/api/tranche9/crossings/source?')));
  ok=false;await load();assert.equal(children.length,0);assert.match(status.textContent,/Unavailable/);
});
