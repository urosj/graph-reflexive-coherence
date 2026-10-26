import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkedLifecycle,lifecycleLoader} from './tranche8-lifecycle.js';
const base=new URL('../../../../../../phase-9-grcv4/tranche-8/',import.meta.url);
const read=name=>JSON.parse(readFileSync(new URL(name,base)));
const tags={C_OS:'COS',C_CI:'CCI',A_CI:'ACI',A_PC:'APC'};
function payload(family='C_OS') {
  const tag=tags[family],accepted=true;
  return {
    schema:'phase9_tranche8_lifecycle_v1',family,checkpoint:'8.5',
    status:accepted?'accepted':'verified_pending_acceptance',user_accepted:accepted,aggregate_closed:false,
    public_specialization_facade:false,retained_integrity_only:true,native_trajectories_rerun:false,
    manifest_digest:read(family==='C_OS'?'P9-8.5-COSInputs.json':`P9-8.5-${tag}-inputs.json`).record_digest,
    acceptance:read(family==='C_OS'?'P9-8.5-COSAcceptance.json':'P9-8.5-FirstGroupAcceptance.json'),
    first_group_closed:true,first_group_acceptance:read('P9-8.5-FirstGroupAcceptance.json'),
    executions:{small:read(`P9-8.5-${tag}-small.json`),large:read(`P9-8.5-${tag}-large.json`)}
  };
}
test('all four pinned records reject edited evidence, acceptance and widened scope',async()=>{
  for(const family of Object.keys(tags)) {
    await checkedLifecycle(payload(family));
    for(const mutate of [v=>v.user_accepted=!v.user_accepted,v=>v.family='C_PC',
      v=>v.first_group_closed=false,v=>v.first_group_acceptance=null,v=>v.public_specialization_facade=true,v=>v.native_trajectories_rerun=true,
      v=>v.executions.small.observations.cases.continuation_reset.clock_preserved=false,
      v=>v.executions.large.observations.readmissions.pop(),
      v=>v.acceptance=v.family==='C_OS'?null:read('P9-8.5-COSAcceptance.json')]) {
      const v=payload(family);mutate(v);await assert.rejects(()=>checkedLifecycle(v));
    }
  }
});
test('family selector renders bounded evidence and clears stale success on failure',async()=>{
  const children=[],container={replaceChildren(){children.length=0;},append(e){children.push(e);}};
  const status={textContent:''};let fail=false,family='C_OS',wrongFamily=false;
  const load=lifecycleLoader(container,status,async url=>{
    assert.match(url,new RegExp('family='+family));
    return {ok:!fail,json:async()=>payload(wrongFamily?'C_OS':family)};
  },()=>({}),()=>family);
  for(family of Object.keys(tags)) {
    await load();assert.match(status.textContent,/verified; accepted/);
    assert(children.some(e=>/no unified public/.test(e.textContent)));
    assert.equal(children.filter(e=>e.href).length,3);
    assert.equal(children.some(e=>/CertificationInconclusive/.test(e.textContent)),family==='C_OS');
  }
  family='A_PC';wrongFamily=true;await load();assert.equal(children.length,0);assert.match(status.textContent,/Wrong selected family/);
  fail=true;await load();assert.equal(children.length,0);assert.match(status.textContent,/Unavailable/);
});
