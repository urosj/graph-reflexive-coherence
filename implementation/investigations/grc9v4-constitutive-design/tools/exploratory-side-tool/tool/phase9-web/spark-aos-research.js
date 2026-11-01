import {canonicalBasin} from './basin.js';

const reportDigest='6d8fdba74099052d7cedb3b102e3bb031b46f28f2754da8de54bb97430cfed62';
const hash=async body=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',
  new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');

export async function checkedSparkAOSResearch(value) {
  const {projection_digest,...body}=value;
  const {record_digest,...report}=value.report??{};
  if(value.schema!=='grc9v4_spark_aos_research_surface_v1' || await hash(body)!==projection_digest ||
     value.report_record_digest!==reportDigest || record_digest!==reportDigest || await hash(report)!==record_digest ||
     report.family!=='A_OS' || report.status!=='demonstrated_bounded_pending_review' ||
     report.accepted_authority!==false || report.G4_accepted!==false || report.native_support_added?.length!==0 ||
     report.proof?.stationary_writer_self_consistent!==true || report.proof?.all_conductance_directions_included!==true ||
     report.full_dimension!==30 || report.conductance_dimension!==16 ||
     JSON.stringify(report.full_physical_state)!=='["C","W_A"]' ||
     JSON.stringify(value.accepted_scientific_families)!=='["C_OS","C_CI","C_PC","C_CI_PC"]' ||
     value.check_mode!=='retained_source_integrity_no_numerical_rerun')
    throw new Error('Unbound A_OS research or changed scientific scope');
  const indexed=[...report.sources];
  if(value.source_refs.length!==indexed.length+1 ||
     JSON.stringify(value.source_refs.slice(1))!==JSON.stringify(indexed))
    throw new Error('Research source index differs from bound report');
  for(const ref of value.source_refs)
    if(!/^(implementation|specs|src)\//.test(ref.path) || ref.path.split('/').includes('..') || !/^[0-9a-f]{64}$/.test(ref.sha256))
      throw new Error('Invalid research source');
  return value;
}

export function sparkAOSResearchLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking A_OS research…';
    try {
      const response=await fetcher('/api/spark-completion/applicability/a-os/research');
      if(!response.ok)throw new Error('A_OS research unavailable');
      const value=await checkedSparkAOSResearch(await response.json());if(ticket!==sequence)return;
      const r=value.report;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','A_OS: bounded source-to-completion result, pending scientific review and adjudication.');
      add('p','The fixed point has a self-consistent conductance writer using final resources and incoming edge weights.');
      add('p','Full-state trap: 14 resource directions and all 16 conductance directions.');
      for(const role of ['current','reset']) {
        const d=r.decisions[role];
        add('p',`${role}: trap entry ${d.first_certified_entry}; two-beat window ends at ${d.target_completion_step}; live gain ${d.local_gain}.`);
      }
      add('p','Expansion preserves every old-edge conductance, seeds the three internal edges at one, and allocates resource shares 1/128, 63/64, 1/128.');
      for(const limit of r.review_limits)add('p',limit);
      for(const ref of value.source_refs) {
        const a=add('a',ref.path.split('/').at(-1));
        a.href='/api/spark-completion/applicability/a-os/research/source?path='+encodeURIComponent(ref.path);
        a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='Retained research sources verified. Native completion and acceptance remain pending.';
    } catch(error) {
      if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);
    }
  };
}

if(typeof document!=='undefined')document.getElementById('spark-aos-research-refresh')?.addEventListener('click',
  sparkAOSResearchLoader(document.getElementById('spark-aos-research-output'),document.getElementById('spark-aos-research-status')));
