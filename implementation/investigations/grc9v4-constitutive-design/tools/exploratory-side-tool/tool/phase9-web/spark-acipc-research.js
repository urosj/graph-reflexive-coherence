import {canonicalBasin} from './basin.js';
const reportDigest='990f529240a26a67a429b806ed20284f0e668b92b39c75674bcad72ff50168ce';
const hash=async body=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',
  new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');

export async function checkedSparkACIPCResearch(value) {
  const {projection_digest,...body}=value;
  const {record_digest,...r}=value.report??{};
  if(value.schema!=='grc9v4_spark_acipc_research_surface_v1' || await hash(body)!==projection_digest ||
     value.report_record_digest!==reportDigest || record_digest!==reportDigest || await hash(r)!==reportDigest ||
     r.family!=='A_CI_PC' || r.status!=='demonstrated_bounded_pending_review' || r.accepted_authority!==false ||
     r.native_completion!==false || r.G4_accepted!==false || r.full_dimension!==76 || r.conductance_dimension!==16 || r.carrier_dimension!==46 ||
     JSON.stringify(r.full_state)!=='["C","W_A","Z_4"]' || r.proof?.incoming_carrier_geometry!==true || r.proof?.both_independent_writers!==true || r.proof?.all_carrier_directions_included!==true ||
     r.proof?.implicit_geometry_derivative!==true || r.proof?.same_selected_source_for_geometry_and_writer!==true ||
     r.proof?.stationary_composite_gain!==2 || r.proof?.PC_derivative_reused!==false || r.proof?.CI_derivative_reused!==false ||
     r.proof?.stationary_writer_self_consistent!==true || r.proof?.OS_derivative_reused!==false ||
     r.proof?.earlier_family_trajectory_reused!==false || r.decisions?.current?.local_gain!==1 || r.decisions?.reset?.local_gain!==0 ||
     JSON.stringify(r.accepted_scientific_families)!=='["C_OS","C_CI","C_PC","C_CI_PC","A_OS","A_CI","A_PC"]' ||
     value.check_mode!=='retained_source_integrity_no_numerical_rerun')
    throw new Error('Unbound A_CI_PC research or changed scientific scope');
  if(value.source_refs.length!==r.sources.length+1 || JSON.stringify(value.source_refs.slice(1))!==JSON.stringify(r.sources))
    throw new Error('A_CI_PC source index differs');
  for(const ref of value.source_refs)
    if(!/^(implementation|specs|src)\//.test(ref.path) || ref.path.split('/').includes('..') || !/^[0-9a-f]{64}$/.test(ref.sha256))
      throw new Error('Invalid A_CI_PC source');
  return value;
}

export function sparkACIPCResearchLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking A_CI_PC research…';
    try {
      const response=await fetcher('/api/spark-completion/applicability/a-ci-pc/research');
      if(!response.ok)throw new Error('A_CI_PC research unavailable');
      const value=await checkedSparkACIPCResearch(await response.json());if(ticket!==sequence)return;
      const r=value.report;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','A_CI_PC: bounded source-to-completion construction, pending scientific review.');
      add('p','The selected joint root includes incoming carrier history. Its source feeds immediate geometry and the separate carrier writer.');
      add('p','Full-state return: 14 resource, 16 conductance and all 46 independent carrier directions.');
      for(const role of ['current','reset']) {
        const d=r.decisions[role];
        add('p',`${role}: entry ${d.first_certified_entry}; two-beat window ends at ${d.target_completion_step}; live gain ${d.local_gain}.`);
      }
      add('p','The C/W anisotropic shape is borrowed from A_OS. All carrier directions, the coupled derivative, source/event reads and both interval trajectories are fresh A_CI_PC evidence.');
      add('p','Old-edge conductances are preserved and three new edges start at one. Whole source carriers are archived and target carriers reset to zero with explicit history loss. Resource shares are 1/128, 63/64, 1/128.');
      for(const limit of r.review_limits)add('p',limit);
      for(const ref of value.source_refs) {
        const a=add('a',ref.path.split('/').at(-1));
        a.href='/api/spark-completion/applicability/a-ci-pc/research/source?path='+encodeURIComponent(ref.path);
        a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='A_CI_PC sources verified. Review pending; seven scientific families remain accepted.';
    } catch(error) {
      if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);
    }
  };
}

if(typeof document!=='undefined')document.getElementById('spark-acipc-research-refresh')?.addEventListener('click',
  sparkACIPCResearchLoader(document.getElementById('spark-acipc-research-output'),document.getElementById('spark-acipc-research-status')));
