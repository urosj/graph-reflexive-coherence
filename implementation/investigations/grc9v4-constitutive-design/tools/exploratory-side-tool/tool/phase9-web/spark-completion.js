import {canonicalBasin} from './basin.js';

export async function checkedSparkCompletion(value) {
  const hash = async body => [...new Uint8Array(await crypto.subtle.digest('SHA-256',
    new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');
  const {projection_digest,...body}=value;
  if(projection_digest!=='90ce1ef665dfd7f7153e0353288b804fe75c287cbcb1c50b63b18aa75cd6d98c' ||
     await hash(body)!==projection_digest || value.schema!=='grc9v4_sc3_spark_surface_v1' ||
     value.scope?.SC3_closed!==true || value.scope.scientific_family!=='C_OS' ||
     value.scope.native_completed_spark_support!==false || value.scope.hierarchy_support!==false ||
     value.scope.G4_accepted!==false || value.scope.native_support_added?.length!==0 ||
     value.scope.aggregate_debts_closed?.length!==0)
    throw new Error('Unbound spark-completion authority or widened scope');
  for(const trace of [...value.claims,...value.debts,...value.objects,...value.contracts]) {
    const {trace_digest,...rest}=trace;
    if(await hash(rest)!==trace_digest || !trace.rows?.length ||
       trace.rows.some(r=>!r.source_ref || !Array.isArray(r.edge_refs)))
      throw new Error('Invalid spark-completion forensic trace');
  }
  return value;
}

export function sparkCompletionLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking scientific authority and propagation…';
    try {
      const response=await fetcher('/api/spark-completion');
      if(!response.ok)throw new Error('Spark-completion authority unavailable');
      const value=await checkedSparkCompletion(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','SC-1–SC-3 research closed: bounded exact-equation C_OS completion, one new stable child. Native completion and G4 are pending.');
      add('p','Retained authority/propagation integrity only; no new numerical execution. Conditional claims remain conditional.');
      for(const trace of [...value.claims,...value.debts,...value.contracts]) {
        const details=add('details','');const title=create('summary');title.textContent=Object.values(trace.query).join(' / ');details.append(title);
        const pre=create('pre');pre.textContent=JSON.stringify(trace,null,2);details.append(pre);
      }
      for(const ref of value.source_refs) {
        if(!/^(implementation|specs)\//.test(ref.path) || ref.path.split('/').includes('..'))throw new Error('Invalid bound source path');
        const link=add('a',ref.path.split('/').at(-1));link.href='/api/spark-completion/source?path='+encodeURIComponent(ref.path);link.target='_blank';link.rel='noopener';add('span',' · ');
      }
      status.textContent='Scientific authority and linked proposal/paper/spec verified. Native work follows separately.';
    } catch(error) {if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined')document.getElementById('spark-completion-refresh')?.addEventListener('click',
  sparkCompletionLoader(document.getElementById('spark-completion-output'),document.getElementById('spark-completion-status')));
