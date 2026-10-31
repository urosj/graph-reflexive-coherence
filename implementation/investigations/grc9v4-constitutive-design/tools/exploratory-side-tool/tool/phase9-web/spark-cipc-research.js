import {canonicalBasin} from './basin.js';

const reportDigest='e6703c2c9dcbc1e25d611a0bdcef4c7646e3855f5c2015bdea81b50ac59f5c2d';
const hash=async body=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',
  new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');

export async function checkedSparkCIPCResearch(value) {
  const {projection_digest,...body}=value;
  const {record_digest,...report}=value.report??{};
  if(value.schema!=='grc9v4_spark_cipc_research_surface_v1' || await hash(body)!==projection_digest ||
     value.report_record_digest!==reportDigest || record_digest!==reportDigest || await hash(report)!==record_digest ||
     report.family!=='C_CI_PC' || report.status!=='demonstrated_bounded_pending_review' ||
     report.accepted_authority!==false || report.G4_accepted!==false || report.native_support_added?.length!==0 ||
     report.proof?.stationary_composite_gain!==2 || report.proof?.same_selected_source_for_geometry_and_writer!==true ||
     report.full_dimension!==60 || report.carrier_dimension!==46 || report.nonzero_carrier_directions_included!==true ||
     JSON.stringify(report.full_physical_state)!=='["C","Z_4"]' ||
     JSON.stringify(value.accepted_scientific_families)!=='["C_OS","C_CI","C_PC"]' ||
     value.check_mode!=='retained_source_integrity_no_numerical_rerun')
    throw new Error('Unbound C_CI_PC research or changed scientific scope');
  const indexed=[...report.sources];
  if(value.source_refs.length!==indexed.length+1 ||
     JSON.stringify(value.source_refs.slice(1))!==JSON.stringify(indexed))
    throw new Error('Research source index differs from bound report');
  for(const ref of value.source_refs)
    if(!/^(implementation|specs|src)\//.test(ref.path) || ref.path.split('/').includes('..') || !/^[0-9a-f]{64}$/.test(ref.sha256))
      throw new Error('Invalid research source');
  return value;
}

export function sparkCIPCResearchLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking C_CI_PC research…';
    try {
      const response=await fetcher('/api/spark-completion/applicability/ci-pc/research');
      if(!response.ok)throw new Error('C_CI_PC research unavailable');
      const value=await checkedSparkCIPCResearch(await response.json());if(ticket!==sequence)return;
      const r=value.report;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','C_CI_PC: bounded source-to-completion result, pending scientific review and adjudication.');
      add('p','One selected source drives immediate geometry and the persistent writer; the stationary composite gain is two.');
      add('p','Full-state trap: 14 resource directions and 46 carrier directions, including nonzero signed carrier perturbations.');
      for(const role of ['current','reset']) {
        const d=r.decisions[role];
        add('p',`${role}: trap entry ${d.first_certified_entry}; two-beat window ends at ${d.target_completion_step}; live gain ${d.local_gain}.`);
      }
      add('p','Expansion archives both source histories and initializes the entire target carrier to zero.');
      for(const limit of r.review_limits)add('p',limit);
      for(const ref of value.source_refs) {
        const a=add('a',ref.path.split('/').at(-1));
        a.href='/api/spark-completion/applicability/ci-pc/research/source?path='+encodeURIComponent(ref.path);
        a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='Retained research sources verified. Native completion and acceptance remain pending.';
    } catch(error) {
      if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);
    }
  };
}

if(typeof document!=='undefined')document.getElementById('spark-cipc-research-refresh')?.addEventListener('click',
  sparkCIPCResearchLoader(document.getElementById('spark-cipc-research-output'),document.getElementById('spark-cipc-research-status')));
