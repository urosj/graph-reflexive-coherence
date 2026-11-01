import {canonicalBasin} from './basin.js';

export async function checkedSparkPC(value) {
  const hash = async body => [...new Uint8Array(await crypto.subtle.digest('SHA-256',
    new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');
  const {projection_digest,...body}=value;
  if(projection_digest!=='3f7489e3d8fd1f97b3bc7f6a6053580bd2ade60c5bfcbf7b0b89924684363796' ||
     await hash(body)!==projection_digest || value.schema!=='grc9v4_spark_pc_surface_v1' ||
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

export function sparkPCLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking accepted C_PC applicability…';
    try {
      const response=await fetcher('/api/spark-completion/applicability/pc');
      if(!response.ok)throw new Error('Spark applicability authority unavailable');
      const value=await checkedSparkPC(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','Accepted bounded scientific constructions: '+value.scope.scientific_families.join(', ')+'. Native completion, hierarchy and G4 remain pending.');
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
        const link=add('a',ref.path.split('/').at(-1));link.href='/api/spark-completion/applicability/pc/source?path='+encodeURIComponent(ref.path);link.target='_blank';link.rel='noopener';add('span',' · ');
      }
      status.textContent='Scoped scientific adjudication and proposal/paper/spec verified. Native work remains separate.';
    } catch(error) {if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined')document.getElementById('spark-pc-refresh')?.addEventListener('click',
  sparkPCLoader(document.getElementById('spark-pc-output'),document.getElementById('spark-pc-status')));
