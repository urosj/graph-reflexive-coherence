const DIGEST='f48d1cc06f8ffdf02285cb158e7e1f3315c75eed1b70a440400688d1022d5822';
const canonical=value=>JSON.stringify(value,(_,v)=>v && typeof v==='object' && !Array.isArray(v)
  ? Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);
export async function checkedHandoff(value) {
  const h=value?.handoff;
  if(value.schema!=='phase9_tranche8_first_group_handoff_v1'||value.family!=='first_group'||value.checkpoint!=='8.4i'
    ||value.other_families_checked!==false||value.native_trajectories_rerun!==false||!h||h.record_digest!==DIGEST)
    throw Error('Missing or widened first-group handoff');
  const {record_digest,...payload}=h;
  const hash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(payload)));
  if(Array.from(new Uint8Array(hash),x=>x.toString(16).padStart(2,'0')).join('')!==DIGEST)
    throw Error('Changed first-group handoff');
  if(!Array.isArray(value.source_refs)||h.source_refs.some(r=>!value.source_refs.some(s=>canonical(s)===canonical(r))))
    throw Error('Missing bound sources');
  return h;
}
export function handoffLoader(container,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let generation=0;
  return async()=>{
    const current=++generation;container.replaceChildren();status.textContent='Checking retained handoff…';
    try {
      const response=await fetcher('/api/tranche8?family=first_group&checkpoint=8.4i');
      if(!response.ok)throw Error('Handoff unavailable');
      const value=await response.json(),h=await checkedHandoff(value);
      if(current!==generation)return;
      const add=(tag,t)=>{const e=create(tag);e.textContent=t;container.append(e);return e;};
      add('p',`First group: ${h.families.map(r=>r.family).join(', ')}. 36 events, 144 target steps, eight final reads; five source steps counted separately.`);
      add('p','8.4i accepted; first-group 8.4 closed. Next: scoped 8.5, then 8.6. All-ten closure remains open. No numerical rerun, public support or arbitrary-graph numerical guarantee.');
      for(const row of h.families){
        const a=add('a',`${row.family} event checkpoint`);
        a.href='/api/tranche8/source?family=first_group&checkpoint=8.4i&path='+encodeURIComponent(row.positive_event);
      }
      const a=add('a','Handoff review');a.href='/api/tranche8/source?family=first_group&checkpoint=8.4i&path='+encodeURIComponent('implementation/phase-9-grcv4/tranche-8/P9-8.4i-FirstGroupReview.md');
      status.textContent='Retained first-group handoff verified.';
    } catch(error){if(current===generation){container.replaceChildren();status.textContent='Unavailable: '+error.message;}}
  };
}
if(typeof document!=='undefined'&&document.querySelector('#tranche8-handoff')){
  const load=handoffLoader(document.querySelector('#tranche8-handoff'),document.querySelector('#tranche8-handoff-status'));
  document.querySelector('#tranche8-handoff-refresh').addEventListener('click',load);
}
