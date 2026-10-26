import {test} from 'node:test';
import assert from 'node:assert/strict';
import {TRANCHE8_APC_EVIDENCE as evidence} from './tranche8-apc-evidence.js';
import {checkedSelectedRuntime,selectedRuntimeLoader} from './tranche8.js';

const element=tag=>({tag,textContent:'',children:[],append(...nodes){this.children.push(...nodes);},replaceChildren(...nodes){this.children=nodes;}});
const text=node=>node.textContent+node.children.map(text).join(' ');

test('A_PC selected panel reports PC mechanisms and bounded scoped acceptance',async()=>{
  const out=element('div'),status=element('p');let fail=false;const urls=[];
  const load=selectedRuntimeLoader('A_PC',out,status,async url=>{
    urls.push(url);return {ok:!fail,json:async()=>structuredClone(evidence)};
  },element);
  await load();assert.deepEqual(urls,['/api/tranche8?family=A_PC&checkpoint=8.4h']);
  assert.match(text(out),/9 events; 36 target steps; 2 final reads/);
  assert.match(text(out),/Accepted: true/);assert.match(text(out),/archive the whole old carrier/);
  assert.match(text(out),/initialize target Z to zero/);assert.match(text(out),/not a uniform trajectory theorem/);
  const links=out.children.at(-1).children.filter(e=>e.tag==='a');
  assert.ok(links.length>0);assert.ok(links.every(e=>e.href.includes('family=A_PC&checkpoint=8.4h&path=')));
  fail=true;await load();assert.equal(out.children.length,0);assert.match(status.textContent,/Unavailable/);
});

test('A_PC rejects widened credit, discarded loss and absent or altered sources',()=>{
  assert.doesNotThrow(()=>checkedSelectedRuntime(evidence,'A_PC'));
  for(const mutate of [v=>v.other_families_checked=true,v=>v.runtime.aggregate_closed=true,
      v=>v.runtime.explicit_carrier_loss_and_zero_target=false,v=>v.runtime.total_target_steps=40,
      v=>v.source_refs=[],v=>v.source_refs[0].sha256='forged']) {
    const bad=structuredClone(evidence);mutate(bad);assert.throws(()=>checkedSelectedRuntime(bad,'A_PC'));
  }
});
