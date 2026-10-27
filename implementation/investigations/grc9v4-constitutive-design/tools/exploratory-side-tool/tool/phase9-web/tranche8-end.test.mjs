import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {endReviewLoader} from './tranche8-end.js';
const read=name=>JSON.parse(readFileSync(new URL('../../../../../../phase-9-grcv4/tranche-8/'+name,import.meta.url)));
const payload={schema:'phase9_tranche8_end_reviews_v1',families:['C_OS','C_CI','A_CI','A_PC'],final_review_user_accepted:true,first_group_closed:true,aggregate_closed:false,
  records:{mechanisms:read('P9-Tranche8-FirstGroupMechanisms.json'),performance:read('P9-Tranche8-FirstGroupPerformance.json')}};
test('final reviews expose limits and clear unavailable or widened results',async()=>{
  const children=[],container={replaceChildren(){children.length=0;},append(x){children.push(x);}};
  const status={textContent:''};let value=structuredClone(payload),ok=true;
  const load=endReviewLoader(container,status,async()=>({ok,json:async()=>value}),()=>({}));
  await load();assert.match(status.textContent,/verified; bounded scope/);
  assert.equal(children.filter(x=>payload.families.includes(x.textContent)).length,4);
  assert(children.some(x=>/large first-pass/.test(x.textContent)));
  assert(children.some(x=>/not uniform robustness/.test(x.textContent)));
  assert.equal(children.filter(x=>x.href?.includes('/api/tranche8/end/source')).length,3);
  value.records.mechanisms.new_support=true;await load();assert.equal(children.length,0);
  assert.match(status.textContent,/Unexpected review claim/);
  ok=false;await load();assert.equal(children.length,0);assert.match(status.textContent,/Unavailable/);
});
