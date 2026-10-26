import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {checkedHandoff,handoffLoader} from './tranche8-handoff.js';
const handoff=JSON.parse(await readFile(new URL('../../../../../../phase-9-grcv4/tranche-8/P9-8.4i-FirstGroup.json',import.meta.url)));
const value={schema:'phase9_tranche8_first_group_handoff_v1',family:'first_group',checkpoint:'8.4i',handoff,source_refs:handoff.source_refs,other_families_checked:false,native_trajectories_rerun:false};
const element=tag=>({tag,textContent:'',children:[],append(...x){this.children.push(...x);},replaceChildren(...x){this.children=x;}});
const text=e=>e.textContent+e.children.map(text).join(' ');
test('first-group handoff renders bounded accepted decision and failure clears it',async()=>{
  const out=element('div'),status=element('p');let ok=true;const urls=[];
  const load=handoffLoader(out,status,async url=>{urls.push(url);return {ok,json:async()=>value};},element);
  await load();assert.match(text(out),/36 events, 144 target steps/);assert.match(text(out),/All-ten closure remains open/);
  assert.equal(urls[0],'/api/tranche8?family=first_group&checkpoint=8.4i');assert.equal(out.children.filter(e=>e.tag==='a').length,5);
  ok=false;await load();assert.equal(out.children.length,0);assert.match(status.textContent,/Unavailable/);
});
test('changed counts, missing sources and widened acceptance reject',async()=>{
  await checkedHandoff(value);
  for(const mutate of [v=>v.handoff.counts.events++,v=>v.handoff.first_group_i_accepted=false,v=>v.handoff.all_ten_8_4_closed=true,v=>v.source_refs=[],v=>v.other_families_checked=true]){
    const bad=structuredClone(value);mutate(bad);await assert.rejects(()=>checkedHandoff(bad));
  }
});
