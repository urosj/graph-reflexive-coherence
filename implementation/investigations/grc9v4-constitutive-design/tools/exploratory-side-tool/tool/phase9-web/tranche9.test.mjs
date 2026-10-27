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
