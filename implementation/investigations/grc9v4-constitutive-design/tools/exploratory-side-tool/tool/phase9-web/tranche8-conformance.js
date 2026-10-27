const ACCEPTANCE_PIN="45e4b5bdabcc2027bce69036ff710861d5e10f865deff7665f9f66500fdbd01c";
const PINS={"first_group":"c5367d4454e4743bde2292f536fd6759ce54271c9d4da32bccf6bdb9cc2a7e55","C_OS":"cce7f942ff83b623721466cf816b422210748ebd9a102f78d1b0590d8f4fad27","C_CI":"87fb05ebf5281a727c4e21e1353d548daeb46e8cdc102112d37ed149defbd983","A_CI":"43a1d873973c7a37a163e5b74dc95c42623b5556215d89910b26987f8f52beff","A_PC":"1ca4d702d02ec58b49d3e0bae2b8ca8e8cc40b1964f689ad7bade78622ca186b"};
const canonical=value=>JSON.stringify(value,(_,v)=>v && typeof v==='object' && !Array.isArray(v)
  ? Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);
export async function checkedConformance(value) {
  const d=value?.decision,pin=PINS[value?.family];
  if(!pin||value.schema!=='phase9_tranche8_conformance_v1'||value.checkpoint!=='8.6'
    ||value.group_record_digest!==PINS.first_group||value.user_accepted!==true
    ||value.first_group_closed!==true||value.aggregate_closed!==false||value.numerical_trajectories_rerun!==false
    ||d?.record_digest!==pin)throw Error('Missing or widened conformance scope');
  const a=value.acceptance;
  if(a?.record_digest!==ACCEPTANCE_PIN||a.decision_digest!==PINS.first_group
    ||a.user_accepted!==true||a.first_group_closed!==true||a.aggregate_closed!==false)
    throw Error('Missing scoped acceptance');
  const {record_digest:acceptanceDigest,...acceptancePayload}=a;
  const ah=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(acceptancePayload)));
  if(Array.from(new Uint8Array(ah),x=>x.toString(16).padStart(2,'0')).join('')!==ACCEPTANCE_PIN)
    throw Error('Changed acceptance');
  const {record_digest,...payload}=d;
  const hash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(payload)));
  if(Array.from(new Uint8Array(hash),x=>x.toString(16).padStart(2,'0')).join('')!==pin)
    throw Error('Changed conformance decision');
  return value.family==='first_group'?d.families:[d];
}
export function conformanceLoader(container,status,fetcher=fetch,create=tag=>document.createElement(tag),selected=()=>'first_group') {
  let generation=0;
  return async()=>{
    const current=++generation,family=selected();container.replaceChildren();status.textContent='Checking retained conformance…';
    try {
      const response=await fetcher('/api/tranche8?family='+encodeURIComponent(family)+'&checkpoint=8.6');
      if(!response.ok)throw Error('Conformance evidence unavailable');
      const value=await response.json(),rows=await checkedConformance(value);
      if(current!==generation)return;
      if(value.family!==family)throw Error('Wrong selected scope');
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;container.append(e);return e;};
      add('p','Bounded conformance accepted for the four-family first group. No arbitrary-graph numerical guarantee, uniform trajectory enclosure or public specialization facade. No numerical rerun.');
      for(const r of rows){
        add('h3',r.family);
        add('p',r.scientific_scope.mechanism);
        add('p',r.scientific_scope.numerical_scope);
        add('p','Limit: '+r.scientific_scope.limitation);
        add('p','Retained exclusion: '+r.scientific_scope.exclusion);
        add('p','Baseline: 10 target steps per role. Each mapped counterpart: 1 per role.');
      }
      const a=add('a','Conformance review');a.href='/api/tranche8/source?family='+encodeURIComponent(family)+'&checkpoint=8.6&path='+encodeURIComponent('implementation/phase-9-grcv4/tranche-8/P9-8.6-FirstGroupReview.md');
      status.textContent='Retained '+family+' conformance verified; bounded first-group acceptance recorded.';
    } catch(error){if(current===generation){container.replaceChildren();status.textContent='Unavailable: '+error.message;}}
  };
}
if(typeof document!=='undefined'&&document.querySelector('#tranche8-conformance')){
  const load=conformanceLoader(document.querySelector('#tranche8-conformance'),document.querySelector('#tranche8-conformance-status'),fetch,tag=>document.createElement(tag),()=>document.querySelector('#tranche8-conformance-family').value);
  document.querySelector('#tranche8-conformance-refresh').addEventListener('click',load);
  document.querySelector('#tranche8-conformance-family').addEventListener('change',load);
}
