// Exact selected execution records; no browser numerical execution or support grant.
const PINS={
  C_OS:{manifest:'ec8206c1728754907aa5fc0fc819bdd5ed71fb6ae8070823bbcdd39a2804e6c4',small:'b10a2e2116dc78458e8cd079d08c284f3545b19617a142e62a7f4ab633ca1f4f',large:'cb779fe08f6f37ee4ddaab0f577415db814cabb559b23963f31038843929ddf3',accepted:true,tag:'COS'},
  C_CI:{manifest:'fd6b94ffabb884eaafc33298d5a1f7f009c7aee5e04d05bb958e6c27dcf27811',small:'9f36f2ce92378688e6cb2f27cd174089d46babecda21ffb5e9e0f3d8162aeb9f',large:'e783fb7cba5c870c78097e035612d2c13db4e194c268f1a2add0cf7cafd8d23b',accepted:true,tag:'CCI'},
  A_CI:{manifest:'77057d852b99efb4c9402d447238e807154e7c7d02a550e4a0ce4ac7ec5a1ef4',small:'08b9710f38da8638b7a6e08a1ee8aae3989df5c3f07b773f8890364a1ca7bab6',large:'307d9e09e903f4426f029448205bc328cdb9e8d9aa5755d8a2fbe8190f9506ee',accepted:true,tag:'ACI'},
  A_PC:{manifest:'fc9e428392101b4f90c603373a394608fee49f5131e4fd2af0d80954f7f9e382',small:'d680faa70dda64293c833770a3ad3796516cf49a23c28b798619b36f528a649b',large:'135741328427e3d0404a919bc2996688ca1111cda7223004e470904a0287d630',accepted:true,tag:'APC'}
};
const GROUP_ACCEPTANCE='64f102670b4a46d0310ac2d2b2f6eca819dafb24203019408fe4e3d2ce42045c';
const ACCEPTANCE='2bc1972e6cf6560a9fc4f4edc6aeca787c4222c655c2c6d4f1304964bc220701';
const canonical=value=>JSON.stringify(value,(_,v)=>v && typeof v==='object' && !Array.isArray(v)
  ? Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);

async function verifyDigest(r,expected) {
  if(!r||r.record_digest!==expected)throw Error('Unbound lifecycle record');
  const {record_digest,...payload}=r;
  const hash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(payload)));
  if(Array.from(new Uint8Array(hash),x=>x.toString(16).padStart(2,'0')).join('')!==expected)
    throw Error('Changed lifecycle record');
}
export async function checkedLifecycle(value) {
  const pins=PINS[value?.family];
  if(!pins||value.schema!=='phase9_tranche8_lifecycle_v1'||value.checkpoint!=='8.5'
    ||value.manifest_digest!==pins.manifest||value.status!==(pins.accepted?'accepted':'verified_pending_acceptance')
    ||value.user_accepted!==pins.accepted||value.aggregate_closed!==false||value.public_specialization_facade!==false
    ||value.retained_integrity_only!==true||value.native_trajectories_rerun!==false)
    throw Error('Missing or widened family lifecycle scope');
  for(const segment of ['small','large']) {
    const r=value.executions?.[segment];
    if(r?.manifest_digest!==pins.manifest||r.family!==value.family)throw Error('Wrong execution family');
    await verifyDigest(r,pins[segment]);
  }
  await verifyDigest(value.acceptance,value.family==='C_OS'?ACCEPTANCE:GROUP_ACCEPTANCE);
  await verifyDigest(value.first_group_acceptance,GROUP_ACCEPTANCE);
  if(value.first_group_closed!==true)throw Error('Missing first-group acceptance');
  return value.executions;
}

export function lifecycleLoader(container,status,fetcher=fetch,create=tag=>document.createElement(tag),selected=()=>'C_OS') {
  let generation=0;
  return async()=>{
    const current=++generation,family=selected();container.replaceChildren();status.textContent='Checking retained '+family+' lifecycle evidence…';
    try {
      const response=await fetcher('/api/tranche8?family='+encodeURIComponent(family)+'&checkpoint=8.5');
      if(!response.ok)throw Error('Lifecycle evidence unavailable');
      const value=await response.json(),records=await checkedLifecycle(value);
      if(current!==generation)return;
      if(family!==value.family)throw Error('Wrong selected family response');
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;container.append(e);return e;};
      add('p',`${records.small.observations.tests} native lifecycle tests passed; larger 107-vertex / 407-edge checkpoint replayed exactly with both-role readmission.`);
      add('p',(value.user_accepted?'Accepted. ':'Pending acceptance. ')+'Internal event owner and explicitly linked generic step/reset owner; no unified public GRC9V4 snapshot or model support claim. First-group 8.5 is accepted; the other six families and all-ten closure remain open.');
      if(family==='C_OS')add('p','Exact split rejection and Arb256 CertificationInconclusive are distinct tested outcomes; both preserve the publication. This view checks retained integrity, not a fresh numerical run.');
      for(const name of Object.keys(records.small.observations.cases))add('p',name.replaceAll('_',' ')+': passed');
      const prefix='implementation/phase-9-grcv4/tranche-8/';
      for(const [label,path] of [['Review',family==='C_OS'?'P9-8.5-COSReview.md':'P9-8.5-'+PINS[family].tag+'-review.md'],['Small execution','P9-8.5-'+PINS[family].tag+'-small.json'],['Large execution','P9-8.5-'+PINS[family].tag+'-large.json']]) {
        const a=add('a',label);a.href='/api/tranche8/source?family='+encodeURIComponent(family)+'&checkpoint=8.5&path='+encodeURIComponent(prefix+path);
      }
      status.textContent='Retained '+family+' 8.5 evidence verified; '+(value.user_accepted?'accepted.':'pending acceptance.');
    } catch(error){if(current===generation){container.replaceChildren();status.textContent='Unavailable: '+error.message;}}
  };
}
if(typeof document!=='undefined'&&document.querySelector('#tranche8-lifecycle')){
  const load=lifecycleLoader(document.querySelector('#tranche8-lifecycle'),document.querySelector('#tranche8-lifecycle-status'),fetch,tag=>document.createElement(tag),()=>document.querySelector('#tranche8-lifecycle-family').value);
  document.querySelector('#tranche8-lifecycle-refresh').addEventListener('click',load);
  document.querySelector('#tranche8-lifecycle-family').addEventListener('change',load);
}
