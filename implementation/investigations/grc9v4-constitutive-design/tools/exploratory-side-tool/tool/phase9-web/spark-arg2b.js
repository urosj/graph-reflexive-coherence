import {canonicalBasin} from './basin.js';

export async function checkedSparkARG2b(value) {
  const hash = async body => [...new Uint8Array(await crypto.subtle.digest('SHA-256',
    new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');
  const {projection_digest,...body}=value;
  if(projection_digest!=='c3088e4da6a5c720087b3f6ab894fd636e90ec7b955e95c1b329a0006b928950' ||
     await hash(body)!==projection_digest || value.schema!=='grc9v4_spark_arg2b_surface_v1' ||
     value.scope.native_completed_spark_support!==false || value.scope.hierarchy_support!==false ||
     value.scope.G4_accepted!==false || value.scope.native_support_added.length!==0 ||
     value.scope.aggregate_debts_closed.length!==0)
    throw new Error('Unbound spark applicability authority or widened scope');
  for(const trace of [...value.claims,...value.debts,...value.objects,...value.contracts]) {
    const {trace_digest,...rest}=trace;
    if(await hash(rest)!==trace_digest || !trace.rows?.length ||
       trace.rows.some(r=>!r.source_ref || !Array.isArray(r.edge_refs)))
      throw new Error('Invalid spark applicability forensic trace');
  }
  return value;
}

export function sparkARG2bLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking accepted A_RG2b applicability…';
    try {
      const response=await fetcher('/api/spark-completion/applicability/a-rg2b');
      if(!response.ok)throw new Error('Spark applicability authority unavailable');
      const value=await checkedSparkARG2b(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','Accepted bounded scientific constructions: '+value.scope.scientific_families.join(', ')+'. Native completion, hierarchy and G4 remain pending.');
      add('p','Direct entry 300 → completion 302 for current and reset at uniform duration 16; last executed step 302, zero subsequent supporting steps. The exact continuous-domain proof covers all 30 resource/conductance directions and the full writer without differentiating Gamma.');
      add('p','Retained authority and propagation integrity; no numerical campaign is rerun.');
      for(const row of value.family_dispositions)
        add('p',row.family+' · '+row.status+' · physical state: '+row.physical_state.join(', '));
      for(const limit of value.review_limits)add('p','Review boundary: '+limit);
      for(const trace of [...value.claims,...value.debts,...value.contracts]) {
        const details=add('details','');const title=create('summary');title.textContent=Object.values(trace.query).join(' / ');details.append(title);
        const pre=create('pre');pre.textContent=JSON.stringify(trace,null,2);details.append(pre);
      }
      for(const ref of value.source_refs) {
        if(!/^(implementation|specs|src)\//.test(ref.path) || ref.path.split('/').includes('..'))throw new Error('Invalid bound source path');
        const link=add('a',ref.path.split('/').at(-1));link.href='/api/spark-completion/applicability/a-rg2b/source?path='+encodeURIComponent(ref.path);link.target='_blank';link.rel='noopener';add('span',' · ');
      }
      status.textContent='Scoped scientific adjudication and proposal/paper/spec verified. Native work remains separate.';
    } catch(error) {if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined')document.getElementById('spark-arg2b-refresh')?.addEventListener('click',
  sparkARG2bLoader(document.getElementById('spark-arg2b-output'),document.getElementById('spark-arg2b-status')));
