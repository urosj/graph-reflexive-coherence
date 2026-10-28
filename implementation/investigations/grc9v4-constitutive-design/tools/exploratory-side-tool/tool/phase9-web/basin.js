import {canonical} from './verification.js';

// The forensic source/trace grammar uses Python ensure_ascii=True, unlike the
// runtime JCS codec. Escape UTF-16 units, including both halves of astral pairs.
export const canonicalBasin = value => canonical(value).replace(/[\u007f-\uffff]/g,
  c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));

export async function checkedBasin(v) {
  const hex = bytes => [...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  const hash = async value => hex(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonicalBasin(value))));
  const {projection_digest,...body}=v;
  if(projection_digest!=="c813d531b9ce83431b53070a03ec7e5b83ffbc36375435f179c5604dbddbb636" || await hash(body)!==projection_digest || v.schema!=='grcv4_p9101a_basin_surface_v1' ||
     v.authority_record_digest!=='409e503e1ba880e2ab17a61f93f950e1a3e3116619561f19e70df9f0fc5eef28' ||
     v.authority_extension_digest!=='b166c00b8ff646c072cb6ddc1187bc975931488f9a0f84f81a7a4ad84ada975c' ||
     v.policy_id!=='grc9v4-terminal-flow-regions-v1' || v.design_accepted!==true ||
     v.native_conformance!==false || v.P9_10_1a_closed!==false || v.full_GRC9V4_conformance!==false ||
     JSON.stringify(v.selected_native_scope)!==JSON.stringify(['C_OS','C_CI','A_CI','A_PC']) ||
     !Array.isArray(v.contracts) || v.contracts.length!==6 || !v.source_refs?.length)
    throw new Error('Unexpected basin authority or widened scope');
  const expected=['INPUTS','MEMBERSHIP','SEEDS','IDENTITY','LIFECYCLE','CEILING'].map(s=>'P9-EC-GRC9-BASIN-'+s);
  if(v.contracts.some((t,i)=>t.query?.contract_id!==expected[i]))throw new Error('Wrong basin contracts');
  for(const trace of [v.claim,v.debt,v.object,...v.contracts]) {
    const {trace_digest,...rest}=trace;
    if(await hash(rest)!==trace_digest || !trace.rows?.length ||
       trace.rows.some(r=>!r.source_ref || !Array.isArray(r.edge_refs)))
      throw new Error('Unbound basin forensic trace');
  }
  if(v.debt.rows[0].payload.status!=='resolved_bounded_design' ||
     !v.debt.rows.some(r=>r.classification==='forward_verification_routing' && r.payload.status==='pending_forward'))
    throw new Error('Missing forward native obligation');
  return v;
}

export function basinLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking accepted basin authority…';
    try {
      const response=await fetcher('/api/basin');if(!response.ok)throw new Error('Authority unavailable');
      const value=await checkedBasin(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','Design accepted; membership/identity design debt resolved. Native interface and lifecycle conformance remain open for C_OS, C_CI, A_CI and A_PC.');
      add('p','Present-flow diagnostic only: no stable attractor, physical basin birth, numeric abundance or spark completion claim.');
      for(const trace of [value.claim,value.debt,value.object,...value.contracts]) {
        add('h3',Object.values(trace.query).join(' / '));
        add('pre',JSON.stringify(trace,null,2));
      }
      for(const ref of value.source_refs) {
        if(!ref.path.startsWith('implementation/') || ref.path.split('/').includes('..'))throw new Error('Invalid source reference');
        const a=add('a',ref.path.split('/').at(-1));a.href='/api/basin/source?path='+encodeURIComponent(ref.path);a.target='_blank';a.rel='noopener';
        add('span',' · ');
      }
      status.textContent='Accepted authority verified; native conformance pending.';
    } catch(error) {if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined') {
  document.getElementById('basin-refresh')?.addEventListener('click',basinLoader(document.getElementById('basin-output'),document.getElementById('basin-status')));
}
